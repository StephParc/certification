from fastapi import FastAPI, Depends
from fastapi import HTTPException, Query, Path

# from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer, String, Float, MetaData, create_engine, and_, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, noload, Session
# from .models import Evenement
# from models import Auteur, Partition, AssAuteurPartition, Evenement, HBM, AssEvenementHbm
from typing import Union, Annotated
from pydantic import BaseModel
from crud import read_event_by_id, create_event, delete_event, update_event
from models import Evenement, SessionLocal
from schemas import Event, EventId
from datetime import datetime, date
from database import get_session

import os
from dotenv import load_dotenv

# Spécifiez le chemin vers votre fichier .env
env_path = os.path.join(os.path.dirname(__file__),'.env')
# Chargez les variables d'environnement depuis le fichier .env
load_dotenv(dotenv_path=env_path)
SQL_DATABASE_URL = os.getenv('SQL_DATABASE_URL')

app = FastAPI()


def session_open():
    engine = create_engine(SQL_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

@app.get("/event/{event_id}", response_model=list[EventId])
def get_event(event_id:int)-> list[Event]:
    session = session_open()
    result= read_event_by_id(session, event_id)
    return result

@app.post("/event/", response_model=EventId)
def create_evenement(event:Event):
    session = session_open()
    evenement=create_event(session, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
    session.commit()
    session.refresh(evenement)
    return evenement

@app.delete("/event/{event_id}")
def del_evenement(id:int):
    session = session_open()
    result = delete_event(session,id)
    session.commit()
    return result

@app.put("/event/{event_id}")
def update_evenement(event:EventId):
    session = session_open()
    result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
    session.commit()
    return result

# @app.get("/items/{item_id}")
# async def read_items(
#     item_id: Annotated[int, Path(title="The ID of the item to get")],
#     q: Annotated[str | None, Query(alias="item-query")] = None,
# ):
#     results = {"item_id": item_id}
#     if q:
#         results.update({"q": q})
#     return results

