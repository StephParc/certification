# evenements.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import  Session
from crud import read_event_by_id,read_event_all, create_event, delete_event, update_event
from schemas import Event, EventId
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/event",
    tags=["Evénement"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/{event_id}", response_model=list[EventId])
def get_event(event_id:int, session:Session=Depends(get_session_sql)):
    return read_event_by_id(session, event_id)

@router.get("/", response_model=list[EventId])
def get_all(session:Session=Depends(get_session_sql)):
    return read_event_all(session)

@router.post("/", response_model=EventId)
def create_evenement(event:Event, session:Session=Depends(get_session_sql)):
    evenement=create_event(session, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
    session.commit()
    session.refresh(evenement)
    return evenement

@router.delete("/{event_id}")
def del_evenement(id:int, session:Session=Depends(get_session_sql)):
    result = delete_event(session,id)
    session.commit()
    return result

@router.put("/{event_id}")
def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
    result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
    session.commit()
    return result

@router.patch("/{event_id}")
def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
    result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
    session.commit()
    return result

