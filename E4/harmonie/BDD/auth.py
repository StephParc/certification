# auth.py
"""
Authentication and Authorization Core Logic.

This module provides the security foundation for the FastAPI application. 
It handles:
1. Password hashing and verification using Bcrypt.
2. JWT (JSON Web Token) generation and decoding.
3. Hierarchical scope-based access control (RBAC).
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from E4.harmonie.BDD.models import User
from E4.harmonie.BDD.schemas import TokenData, UserPass
from E4.harmonie.BDD.database import get_session_sql, sql_connect

# Configuration for password hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated= "auto")

# OAuth2 scheme definition pointing to the login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login",
    description="Enter your username and password to receive a JWT token."
)

def verify_password(plain_password, hashed_password):
    """Checks a plain text password against a hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generates a secure Bcrypt hash from a string."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a signed JWT access token.

    Args:
        data (dict): The payload to encode (typically 'sub' and 'scopes').
        expires_delta (timedelta, optional): Custom expiration time.

    Returns:
        str: An encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session_sql)):
    """
    Validates the JWT token and checks for required security scopes.

    This function implements a hierarchy of permissions:
    - 'full_admin' bypasses all specific scope checks.
    - 'user_admin' covers both user management and read-only tasks.
    - 'read_only' is the minimum required level for GET operations.

    Args:
        security_scopes (SecurityScopes): Scopes required by the API endpoint.
        token (str): The JWT token provided in the Authorization header.

    Raises:
        HTTPException: 401 for invalid credentials or 403 for insufficient permissions.

    Returns:
        User: The authenticated SQLAlchemy user object.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        pseudo = payload.get("sub")
        if pseudo is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, pseudo=pseudo)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = session.query(User).filter_by(pseudo = token_data.pseudo).first()
    if user is None:
        raise credentials_exception

    # Logic-level Hierarchy Implementation
    is_full_admin = "full_admin" in token_data.scopes
    is_user_admin = "user_admin" in token_data.scopes
    is_read_only = "read_only" in token_data.scopes

    for scope in security_scopes.scopes:
        if is_full_admin:
            continue # Full access granted
        
        if is_user_admin and scope in ["user_admin", "read_only"]:
            continue # Admin tasks granted
            
        if is_read_only and scope == "read_only":
            continue # Global read access granted
            
        # If no conditions are met, access is forbidden
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{scope}' manquante",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user
