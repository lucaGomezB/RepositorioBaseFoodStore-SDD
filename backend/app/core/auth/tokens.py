# JWT Token handling
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with user data to encode (user_id, email, rol_id)
        expires_delta: Optional custom expiration (default: 15 minutes)
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp()), "type": "access", "jti": uuid.uuid4().hex[:16]})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary with user data to encode
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": int(expire.timestamp()), "type": "refresh", "jti": uuid.uuid4().hex[:16]})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify token type (access vs refresh).
    
    Args:
        token: JWT token string
        expected_type: Expected type ('access' or 'refresh')
        
    Returns:
        True if token type matches, False otherwise
    """
    payload = decode_token(token)
    if not payload:
        return False
    
    return payload.get("type") == expected_type


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Check if a token payload has expired.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        True if expired, False otherwise
    """
    exp = payload.get("exp")
    if not exp:
        return True
    
    # Handle both string and datetime formats
    if isinstance(exp, str):
        exp_datetime = datetime.fromisoformat(exp.replace("Z", "+00:00"))
    else:
        exp_datetime = exp
    
    return datetime.utcnow() > exp_datetime