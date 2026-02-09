# schemas_mongo.py
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional
import uuid

class CompetenceSchema(BaseModel):
    instrument: str | None = None
    niveau: str | None = None
    polyvalence_poids: int | None = None
    details: List[str] | None = None
    # instrument_uuid: uuid.UUID | None = None # Optionnel : lien vers TB_instrument

    model_config = ConfigDict(from_attributes=True)

class MusicianMongoSchema(BaseModel):
    user_uuid: uuid.UUID | None = None # Le pont vers TB_users
    pseudo: str | None = None
    nom: str | None = None
    prenom: str | None = None
    email: EmailStr | None = None
    accord_donnees_perso: bool = False
    competences: List[CompetenceSchema] | None = None
    statut: str | None = "actif"

    model_config = ConfigDict(from_attributes=True)