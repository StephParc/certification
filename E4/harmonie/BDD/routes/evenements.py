# evenements.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import  Session
from crud import read_event_by_id, read_event_by_date, read_event_by_year, read_event_by_type, read_event_by_partition, read_event_all
from crud import create_event, delete_event, update_event
from schemas import Event, EventId , TypeEvent
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

@router.get("/by_date/", response_model=list[EventId])
def get_event_by_date(event_date:str=Query(description="Date au format YYYY-MM-DD"), session:Session=Depends(get_session_sql)):
    return read_event_by_date(session, event_date)

@router.get("/by_year/", response_model=list[list[EventId]])
def get_event_by_year(year:int, session:Session=Depends(get_session_sql)):
    return read_event_by_year(session, year)

@router.get("/by_type/", response_model=list[list[EventId]])
def get_event_by_type(type_event:TypeEvent, session:Session=Depends(get_session_sql)):
    return read_event_by_type(session, type_event)

@router.get("/by_partition_hbm_id/", response_model=list[list[EventId]])
def get_event_by_partition_hbm_id(id:int, session:Session=Depends(get_session_sql)):
    return read_event_by_partition(session, id)

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

@router.get("/", response_model=list[EventId])
def get_all(session:Session=Depends(get_session_sql)):
    return read_event_all(session)
