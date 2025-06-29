# users.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session
from crud import create_user, read_user_by_id, read_user_by_username, update_user_sample, update_user_complete, delete_user
from schemas import UserAdmin, UserPass, UserPublic
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/users",
    tags=["Utilisateur"],
    # dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/by_id/{user_id}", response_model=list[UserAdmin])
def get_user(user_id:int, session:Session=Depends(get_session_sql), dependancies=Security(get_current_user,scopes=["read_only"])):
    return read_user_by_id(session, user_id)

@router.get("/by_username/{username}", response_model=UserPublic)
def get_user_public(username:str, session:Session=Depends(get_session_sql)):
    return read_user_by_username(session, username)
   
@router.post("/", response_model=UserPublic)
def create_utilisateur(user:UserPass, session:Session=Depends(get_session_sql)):
    user = create_user(session, user.username, user.password, user.fullname, user.email)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
def del_user(id:int, session:Session=Depends(get_session_sql)):
    result = delete_user(session,id)
    session.commit()
    return result

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


