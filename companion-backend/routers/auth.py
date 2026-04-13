import os
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Body, Depends

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
CARER_USERNAME = os.environ.get("CARER_USERNAME", "carer")
CARER_PASSWORD = os.environ.get("CARER_PASSWORD", "")


def create_access_token(data: dict) -> str:
    """Create a JWT token with 24 hour expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    from jose import jwt
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> dict or None:
    """Decode and verify JWT token"""
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def get_current_carer(authorization: str = Header(None, alias="Authorization")):
    """FastAPI dependency to get current authenticated carrier"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


@router.post("/auth/login")
async def login(username: str = Body(...), password: str = Body(...)):
    """Authenticate carrier and return JWT token"""
    if not CARER_PASSWORD:
        logger.warning("CARER_PASSWORD not configured")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if username != CARER_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if password != CARER_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": username, "user_id": 1})
    
    return {"token": token, "username": username}