# authentication.py
"""
Authentication and Authorization Router.

This module implements the OAuth2 password flow for user authentication. 
It provides the endpoint to exchange user credentials (username/password) 
for a JWT access token containing specific security scopes.

Security:
    - Implements stateless JWT (JSON Web Token) authentication.
    - Access tokens include user-specific 'scopes' retrieved from the database permissions.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import  Session

from config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from E4.harmonie.BDD.auth import verify_password, create_access_token, get_current_user
from E4.harmonie.BDD.database import get_session_sql
from E4.harmonie.BDD.models import User

from pydantic import BaseModel, ValidationError


router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
    # dependencies=[Depends()],
    responses={404: {"description":"Not found"}},
)

@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session_sql)):
    """
    Validate credentials and return a JWT access token.
    
    Checks the database for the provided pseudo and verifies the hashed password. 
    If valid, generates a token with the user's defined scopes.
    """
    user = session.query(User).filter(User.pseudo == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract permissions to include in the token payload
    user_permissions = user.permissions.split() if user.permissions else []

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.pseudo, "scopes": user_permissions}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token":access_token, "token_type":"bearer", "scope": " ".join(user_permissions)}

