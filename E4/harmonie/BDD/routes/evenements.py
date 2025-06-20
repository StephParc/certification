from fastapi import APIRouter, Depends
from sqlalchemy.orm import  Session
from ..crud import read_event_by_id, create_event, delete_event, update_event
# from schemas import Event, EventId
# from database import get_session_sql

# router = APIRouter(
#     prefix="/event",
#     # tags="Evénements",
#     # dependencies=[Depends()],
#     # responses={404: {"description":"Not found"}},
# )

# @router.get("/{event_id}", response_model=list[EventId])
# def get_event(event_id:int, session:Session=Depends(get_session_sql))-> list[Event]:
#     result= read_event_by_id(session, event_id)
#     return result