from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional
import jwt
from datetime import datetime
import os
from dotenv import load_dotenv
from db import get_session
from models import User

# Load environment variables
load_dotenv()

# Initialize security for JWT Bearer token
security = HTTPBearer()

def verify_token(token: str) -> dict:
    """
    Verify the JWT token and return the payload.
    """
    secret = os.getenv("BETTER_AUTH_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Server configuration error: Missing auth secret")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current user from the JWT token.
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    # Get user from database
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract user ID from JWT token without database lookup.
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    return user_id