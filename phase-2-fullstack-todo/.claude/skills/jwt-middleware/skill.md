 # JWT Middleware Skill

  ## Purpose
  Implement JWT token verification middleware for FastAPI with proper error handling.

  ## Context
  Used to authenticate API requests by verifying JWT tokens in Authorization header.

  ## Pattern
  ```python
  from fastapi import Request, HTTPException
  from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  from jose import JWTError, jwt
  import os

  security = HTTPBearer()

  async def jwt_middleware(request: Request, call_next):
      # Skip auth routes
      if request.url.path.startswith("/auth"):
          return await call_next(request)

      # Extract token
      auth_header = request.headers.get("Authorization")
      if not auth_header or not auth_header.startswith("Bearer "):
          raise HTTPException(status_code=401, detail="Missing or invalid token")

      token = auth_header.split(" ")[1]

      try:
          # Verify and decode
          payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
          request.state.user_id = payload.get("sub")
          request.state.email = payload.get("email")
      except JWTError:
          raise HTTPException(status_code=401, detail="Invalid or expired token")

      return await call_next(request)

  Best Practices

  - Use HTTPBearer for security scheme
  - Verify token signature with shared secret
  - Check token expiration
  - Attach user context to request.state
  - Return proper HTTP status codes
  - Skip middleware for public routes

  Validation

  - Valid tokens pass through
  - Expired tokens rejected with 401
  - Missing tokens rejected with 401
  - Malformed tokens rejected with 400
  - User context accessible in routes
