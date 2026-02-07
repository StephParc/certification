# musiciens.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from E4.harmonie.BDD import crud_mongo
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.schemas_mongo import MusicianMongoSchema

router = APIRouter(prefix="/musiciens", tags=["Musiciens"])

@router.get("/", response_model=List[MusicianMongoSchema])
async def list_musicians(current_user = Depends(get_current_user)):
    """
    Liste les musiciens selon les droits :
    - Admin : Voit tout.
    - Musicien : Voit ceux qui ont accepté + lui-même.
    """
    is_admin = current_user.permissions == "admin"
    requester_uuid = str(current_user.user_uuid)
    
    # On utilise la logique de filtrage Mongo
    musicians = crud_mongo.get_visible_musicians(requester_uuid, is_admin)
    return musicians

@router.get("/{target_uuid}", response_model=MusicianMongoSchema)
async def get_musician(target_uuid: str, current_user = Depends(get_current_user)):
    # Logique de récupération et check de sécurité (voir message précédent)
    # ...
    return musician