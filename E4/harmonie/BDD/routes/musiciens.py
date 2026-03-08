# musiciens.py
from fastapi import APIRouter, Depends, HTTPException, Security
from typing import List
from E4.harmonie.BDD.crud_mongo import get_one_document,get_visible_musicians,update_one_document
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.schemas_mongo import MusicianID, MusicianBase

router = APIRouter(
    prefix="/musiciens", 
    tags=["Musiciens"])

@router.get("/", response_model=List[MusicianID])
def list_musicians(current_user = Security(get_current_user, scopes=["read_only"])):
    """
    Liste les musiciens selon les droits :
    - Admin : Voit tout.
    - Musicien : Voit ceux qui ont accepté + lui-même.
    """
    is_admin = "full_admin" in (current_user.permissions or "")
    requester_uuid = str(current_user.user_uuid)
    
    musicians = get_visible_musicians(requester_uuid, is_admin)
    return musicians

@router.get("/{target_uuid}", response_model=MusicianID)
def get_musician(target_uuid: str, current_user = Security(get_current_user, scopes=["read_only"])):
    musician = get_one_document("COL_musiciens", {"user_uuid": target_uuid})
    
    if not musician:
        raise HTTPException(status_code=404, detail="Musicien non trouvé")

    is_admin = "full_admin" in (current_user.permissions or "")
    is_own_profile = str(current_user.user_uuid) == target_uuid
    has_consented = musician.get("accord_donnees_perso", False)

    if not (is_admin or is_own_profile or has_consented):
        raise HTTPException(status_code=403, detail="Accès refusé (RGPD)")

    return musician

@router.put("/me", response_model=bool)
def update_my_profile(data: MusicianBase, current_user = Security(get_current_user, scopes=["read_only"])):
    """Permet à un musicien de mettre à jour ses propres données."""
    requester_uuid = str(current_user.user_uuid) #
    
    # On utilise model_dump(exclude_unset=True) pour ne modifier que les champs envoyés
    success = update_one_document(
        "COL_musiciens", 
        {"user_uuid": requester_uuid}, 
        data.model_dump(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return success