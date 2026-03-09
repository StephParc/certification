# auteurs.py
"""
API Router for Author Management.

This module handles CRUD operations for Authors (Composers, Arrangers, 
and Artists). It provides endpoints to list all creators, retrieve 
details by ID, and register new authors in the database.

Security:
    - Default: 'read_only' scope required for data retrieval.
    - Administrative: 'full_admin' scope required for creation and deletion.
"""
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session

from E4.harmonie.BDD.crud import create_auteur, read_auteur_all,read_auteur_by_id, delete_auteur
from E4.harmonie.BDD.schemas import Auteur, AuteurId
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.database import get_session_sql

router = APIRouter(
    prefix="/auteurs",
    tags=["Auteur: Compositeur/Arrangeur/Artiste"],
    dependencies=[Security(get_current_user,scopes=["read_only"])],
    responses={404: {"description":"Not found"}}
)   

@router.get("/", response_model=list[AuteurId])
def get_auteur_all(session:Session=Depends(get_session_sql)):
    return read_auteur_all(session)
    
@router.get("/{auteur_id}", response_model=list[AuteurId])
def get_auteur_by_id(auteur_id:int, session:Session=Depends(get_session_sql)):
    return read_auteur_by_id(session, auteur_id)

@router.post("/")
def create_autor(auteur:Auteur, session:Session=Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    autor=create_auteur(session, nom=auteur.nom, prenom=auteur.prenom, pays=auteur.pays, IPI=auteur.IPI, ISNI=auteur.ISNI)
    session.commit()
    session.refresh(autor)
    return autor

@router.delete("/{auteur_id}")
def del_auteur(auteur_id:int, session:Session=Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    result = delete_auteur(session,auteur_id)
    if "succès" in result.lower():
        session.commit()
        return {"statut": "success", "message": result}
    return {"status": "error", "message": result}

# @router.put("/{event_id}")
# def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
#     result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
#     session.commit()
#     return result

# @router.patch("/{event_id}")
# def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
#     result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
#     session.commit()
#     return result