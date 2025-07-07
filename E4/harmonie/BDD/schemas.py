# schema.py . Contient les modèles Pydantic.
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

# pour aller plus loin
class TypeEvent(str, Enum):
    concert = "concert"
    defile = "défilé"
    concert_defile = "concert + défilé"
    sonnerie = "sonnerie"
    autre = "autre prestation"

class Event(BaseModel):
    date_evenement: date | None
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

class Auteur(BaseModel):
    nom : str | None = None
    prenom: str | None = None
    pays: str | None = None
    IPI : str | None = None
    ISNI : str | None = None

    class Config:
        orm_mode=True

class AuteurId(Auteur):
    auteur_id : int | None = None

class Partition(BaseModel):
    titre : str | None = None
    sous_titre : str | None = None
    edition : str | None = None
    collection : str | None = None
    instrumentation : str | None = None
    niveau: float | None = None
    genre : str | None = None
    style : str | None = None
    annee_sortie : int | None = None
    ISMN : str | None = None
    ref_editeur : str | None = None
    duree : str | None = None
    description : str | None = None
    url : str | None = None

    class Config:
        orm_mode=True

class PartitionID(Partition):
    partition_id : int | None = None

class Role(str, Enum):
    compositeur = "compositeur"
    arrangeur = "arrangeur"
    artiste = "artiste"

class AuteurPartition(BaseModel):
    auteur_id: int
    partition_id: int

class AssoAuteurPartition(AuteurPartition):
    role: str

class PartitionHBM(BaseModel):
    partition_id: int | None = None
    distribution: date | None = None
    rendue: bool | None = False
    archive: int | None = None
    concert: bool | None = True
    defile: bool | None = False 
    sonnerie: bool | None = False

class PartitionHbmID(PartitionHBM):
    partition_hbm_id : int 

class PartitionEvent(BaseModel):
    evenement_id : int | None = None
    partition_hbm_id : int | None = None

    class Config:
        orm_mode=True

# class Combo(BaseModel):
#     partition: List[PartitionID]
#     auteur: Dict["auteur":List[Auteur], "role": AssoAuteurPartition]

class UserPublic(BaseModel):
    username: str | None = None
    fullname: str | None = None
    email: str | None = None

    class Config:
        orm_mode=True

class UserPass(UserPublic):
    password: str

class UserAdmin(UserPublic):
    user_id: int | None = None
    permissions: str | None = None
    hashed_password: str | None =None
    scopes: list[str] | None = []

    class Config:
        orm_mode=True

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []