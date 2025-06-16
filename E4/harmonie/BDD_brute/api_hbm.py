from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer, String, Float, MetaData, create_engine, and_, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, noload
# from .models import Evenement
# from models import Auteur, Partition, AssAuteurPartition, Evenement, HBM, AssEvenementHbm
from typing import Union
from pydantic import BaseModel
from .crud import read_event_by_id
from .models import Evenement

import os
from dotenv import load_dotenv

# Spécifiez le chemin vers votre fichier .env
env_path = os.path.join(os.path.dirname(__file__),'.env')
# Chargez les variables d'environnement depuis le fichier .env
load_dotenv(dotenv_path=env_path)
DATABASE_URL = os.getenv('DATABASE_URL')

app = FastAPI()

def session_open():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/event/unique")
def get_event_by_id(event_id:int):
    session = session_open()
    stmt = select(Evenement()).options(noload('*')).where(Evenement().evenement_id==event_id)
    result = session.execute(stmt)
    evenement = result.first()
    session.close()
    return {"Hello": event_id}

@app.get("/event/module")
def get_event(event_id:int):
    session = session_open()
    read_event_by_id(session, event_id)
    return {"hello": event_id}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}