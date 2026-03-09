# users.py
"""
API Router for User Administration.

This module provides administrative endpoints for managing system users. 
It handles the creation of administrative accounts, public profile 
lookups, and user deletion. 

Security:
    - Global Dependency: 'user_admin' scope required for all endpoints.
    - Handles password hashing indirectly through the 'create_user_admin' CRUD function.
"""
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import  Session

from E4.harmonie.BDD.crud import create_user_admin, read_user_by_id, read_user_by_pseudo, update_user_sample, update_user_complete, delete_user
from E4.harmonie.BDD.schemas import UserAdmin, UserPass, UserPublic
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.database import get_session_sql

router = APIRouter(
    prefix="/users",
    tags=["Utilisateur"],
    dependencies=[Security(get_current_user,scopes=["user_admin"])],
    responses={404: {"description":"Not found"}},
)

@router.get("/by_id/{user_id}", response_model=list[UserAdmin])
def get_user(user_id:int, session:Session=Depends(get_session_sql)):
    """Retrieves detailed administrative data for a user by their unique ID."""
    return read_user_by_id(session, user_id)

@router.get("/by_pseudo/{pseudo}", response_model=UserPublic)
def get_user_public(pseudo:str, session:Session=Depends(get_session_sql)):
    """
    Retrieves the public profile of a user by their pseudonym.
    Raises 404 if the user does not exist in the database.
    """
    user = read_user_by_pseudo(session, pseudo=pseudo)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user
   
@router.post("/", response_model=UserAdmin)
def create_utilisateur(user:UserPass, session:Session=Depends(get_session_sql)):
    """
    Registers a new user with administrative privileges.
    
    Includes automatic validation of the creation result and performs 
    a session commit upon success.
    """
    user = create_user_admin(session, pseudo=user.pseudo, password=user.password, fullname=user.fullname, email=user.email, permissions=user.permissions)
    
    if isinstance(user, str): # Si ta fonction renvoie un message d'erreur
        raise HTTPException(status_code=400, detail=user)

    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
def del_user(user_id:int, session:Session=Depends(get_session_sql)):
    """
    Deletes a user account from the system.
    Returns a success or error message based on the database operation outcome.
    """
    result = delete_user(session,user_id)
    if result and "succès" in result.lower():
        session.commit()
        return {"status": "success", "message": result}
    
    return {"status": "error", "message": result}

# @router.patch("/{username}")
# def update_user_by_user(user:UserPublic, session:Session=Depends(get_session_sql)):
#     result = update_user_sample(session, user.username, user.fullname, user.password, user.email)
#     session.commit()
#     return result

# @router.patch("/{user_id}")
# def update_user_by_admin(user:UserAdmin, session:Session=Depends(get_session_sql)):
#     result = update_user_complete(session, user.user_id, user.username, user.fullname, user.email, user.permissions)
#     session.commit()
#     return result


