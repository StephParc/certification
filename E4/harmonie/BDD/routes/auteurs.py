# auteurs.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session
from crud import create_auteur, read_auteur_all,read_auteur_by_id, delete_auteur
from schemas import Auteur, AuteurId
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/auteurs",
    tags=["Auteur: Compositeur/Arrangeur/Artiste"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)   

@router.get("/", response_model=list[AuteurId])
def get_auteur_all(session:Session=Depends(get_session_sql)):
    return read_auteur_all(session)
    
@router.get("/{auteur_id}", response_model=list[AuteurId])
def get_auteur_by_id(id:int, session:Session=Depends(get_session_sql)):
    return read_auteur_by_id(session, id)

@router.post("/")
def create_autor(auteur:Auteur, session:Session=Depends(get_session_sql)):
    autor=create_auteur(session, auteur.nom, auteur.prenom, auteur.pays, auteur.IPI, auteur.ISNI)
    session.commit()
    session.refresh(autor)
    return autor

@router.delete("/{auteur_id}")
def del_auteur(id:int, session:Session=Depends(get_session_sql)):
    result = delete_auteur(session,id)
    session.commit()
    return result

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