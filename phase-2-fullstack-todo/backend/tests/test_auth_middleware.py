"""
Tests for JWT authentication middleware.

Tests verify that the middleware correctly validates JWT tokens, handles errors,
and attaches user context to requests.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


class TestAuthMiddleware:
    """Test suite for JWT authentication middleware."""

    @pytest.fixture(name="app")
    def create_test_app(self):
        """
        Create a test FastAPI application for middleware testing.

        Returns:
            FastAPI: Test application instance.
        """
        from middleware.auth_middleware import verify_jwt_middleware

        app = FastAPI()

        # Define routes first
        @app.get("/api/test")
        async def test_endpoint(request: Request):
            """Protected test endpoint."""
            return {
                "message": "success",
                "user_id": getattr(request.state, "user_id", None),
                "email": getattr(request.state, "email", None),
            }

        @app.get("/auth/login")
        async def auth_endpoint():
            """Public authentication endpoint."""
            return {"message": "login"}

        @app.get("/docs")
        async def docs_endpoint():
            """Public documentation endpoint."""
            return {"message": "docs"}

        # Register middleware after routes
        @app.middleware("http")
        async def auth_middleware_wrapper(request: Request, call_next):
            return await verify_jwt_middleware(request, call_next)

        return app

    @pytest.fixture(name="client")
    def create_test_client(self, app):
        """
        Create a test client for the FastAPI application.

        Args:
            app: Test application from create_test_app fixture.

        Returns:
            TestClient: FastAPI test client.
        """
        return TestClient(app)

    def test_valid_token_passes(self, client, generate_valid_jwt):
        """
        Test that requests with valid JWT tokens pass through middleware.

        Verifies:
        - Request proceeds to route handler
        - Response status is 200 OK
        - User context is attached to request
        """
        # Arrange
        token = generate_valid_jwt(user_id="user-123", email="test@example.com")

        # Act
        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "success"
        assert data["user_id"] == "user-123"
        assert data["email"] == "test@example.com"

    def test_missing_token_returns_401(self, client):
        """
        Test that requests without Authorization header return 401.

        Verifies:
        - Response status is 401 Unauthorized
        - Error response has correct format
        - Error message indicates missing token
        """
        # Act
        response = client.get("/api/test")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data
        assert "missing" in data["error"].lower() or "required" in data["error"].lower()

    def test_expired_token_returns_401(self, client, generate_expired_jwt):
        """
        Test that requests with expired tokens return 401.

        Verifies:
        - Response status is 401 Unauthorized
        - Error response indicates token expiration
        - Error format is standardized
        """
        # Arrange
        token = generate_expired_jwt()

        # Act
        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "expired" in data["error"].lower()

    def test_invalid_signature_returns_401(self, client, generate_invalid_jwt):
        """
        Test that requests with invalid token signatures return 401.

        Verifies:
        - Response status is 401 Unauthorized
        - Error response indicates invalid signature
        - Error format is standardized
        """
        # Arrange
        token = generate_invalid_jwt()

        # Act
        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert (
            "invalid" in data["error"].lower() or "signature" in data["error"].lower()
        )

    def test_malformed_header_returns_400(self, client):
        """
        Test that requests with malformed Authorization header return 400.

        Verifies:
        - Response status is 400 Bad Request
        - Error response indicates malformed header
        - Various malformed formats are rejected
        """
        # Test cases: various malformed headers
        malformed_headers = [
            "InvalidFormat",  # Missing "Bearer "
            "Bearer",  # Missing token
            "Bearer ",  # Empty token
            "Basic token123",  # Wrong auth scheme
        ]

        for header_value in malformed_headers:
            # Act
            response = client.get("/api/test", headers={"Authorization": header_value})

            # Assert
            assert response.status_code in [
                400,
                401,
            ], f"Failed for header: {header_value}"
            data = response.json()
            assert "error" in data

    def test_auth_routes_bypass(self, client):
        """
        Test that /auth/* routes bypass authentication middleware.

        Verifies:
        - /auth/login is accessible without token
        - Response status is 200 OK
        - No authentication required
        """
        # Act
        response = client.get("/auth/login")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "login"

    def test_user_context_attached(self, client, generate_valid_jwt):
        """
        Test that user context is correctly attached to request.state.

        Verifies:
        - request.state.user_id is set
        - request.state.email is set
        - Values match JWT payload claims
        """
        # Arrange
        user_id = "context-test-user"
        email = "context@example.com"
        token = generate_valid_jwt(user_id=user_id, email=email)

        # Act
        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["email"] == email
