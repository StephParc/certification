from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

#exemple
# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str

class Event(BaseModel):
    # evenement_id: int | None =None
    date_evenement: date | None = None# ? ou datetime
    nom_evenement: str | None = None
    lieu: str | None = None
    type_evenement: str | None = None
    affiche: str | None = None

    class Config:
        orm_mode=True

class EventId(Event):
    evenement_id: int | None = None

    class Config:
        orm_mode=True