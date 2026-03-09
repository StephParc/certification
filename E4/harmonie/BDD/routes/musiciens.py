# musiciens.py
"""
API Router for Musician Profile Management (MongoDB).

This module manages musician profiles stored in the NoSQL database. 
It implements strict data visibility rules to ensure GDPR (RGPD) compliance:
- Administrators can view all profiles.
- Users can view their own profile and profiles of musicians who 
  have provided explicit consent (accord_donnees_perso).
- Musicians can update their own personal information.

Security:
    - Default: 'read_only' scope required for all access.
    - Privacy: Logic-level filtering based on user UUID and consent status.
"""
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
    Lists musicians based on access rights:
    - Admin: Full visibility of the collection.
    - Musician: Visible profiles (consented) plus their own.
    """
    is_admin = "full_admin" in (current_user.permissions or "")
    requester_uuid = str(current_user.user_uuid)
    
    musicians = get_visible_musicians(requester_uuid, is_admin)
    return musicians

@router.get("/{target_uuid}", response_model=MusicianID)
def get_musician(target_uuid: str, current_user = Security(get_current_user, scopes=["read_only"])):
    """
    Retrieves a specific musician profile with privacy checks.
    
    Access is granted if the requester is an admin, the profile owner, 
    or if the target has consented to share their data.
    """
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
    """
    Allows a musician to update their own profile data.
    
    Uses 'exclude_unset=True' to perform partial updates on MongoDB documents.
    """
    requester_uuid = str(current_user.user_uuid) #
    
    success = update_one_document(
        "COL_musiciens", 
        {"user_uuid": requester_uuid}, 
        data.model_dump(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return success