# schemas_mongo.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class CompetenceSchema(BaseModel):
    instrument: str
    niveau: str
    polyvalence_poids: int
    details: Optional[List[str]] = None

class MusicianMongoSchema(BaseModel):
    user_uuid: str
    pseudo: str
    nom: str
    prenom: str
    email: EmailStr
    accord_donnees_perso: bool = False
    competences: List[CompetenceSchema]
    statut: str = "actif"

    class Config:
        # Permet de mapper facilement les dictionnaires Mongo
        from_attributes = True