# schemas_mongo.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field, BeforeValidator
from typing import List, Annotated
import uuid
from E4.harmonie.BDD.schemas import PartitionID, PartitionHbmID

PyObjectId = Annotated[str, BeforeValidator(str)]

class CompetenceSchema(BaseModel):
    instrument: str | None = None
    niveau: str | None = None
    polyvalence_poids: int | None = None
    details: List[str] | None = Field(default_factory=list)
    # instrument_uuid: uuid.UUID | None = None # Optionnel : lien vers TB_instrument

    model_config = ConfigDict(from_attributes=True)

class MusicianBase(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    email: EmailStr | None = None
    accord_donnees_perso: bool = False
    competences: list[CompetenceSchema] | None = Field(default_factory=list)
    statut: str | None = "actif"

class MusicianCreate(MusicianBase):
    """Utilisé pour la création initiale ou l'import"""
    pass

class MusicianID(MusicianBase):
    id: PyObjectId | None = Field(default=None, alias="_id")
    user_uuid: uuid.UUID | None = None # Le pont vers TB_users
    pseudo: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True, # Permet d'utiliser 'id' ou '_id' lors de la création
        arbitrary_types_allowed=True
        )

class InstrumentSchema(BaseModel):
    nom_sql: str
    synonymes: list[str] | dict[str, list[str]] | None = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class InstrumentSchemaID(InstrumentSchema):
    id: PyObjectId | None = Field(default=None, alias="_id")
    instrument_uuid: str | uuid.UUID | None = None 
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SubstitutionSchema(BaseModel):   
    sous_famille: str | None = None
    ordre: list[str]

class SubstitutionSchemaID(SubstitutionSchema):
    id: PyObjectId | None = Field(default=None, alias="_id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class NomenclatureItem(BaseModel):
    instrument: str
    priorite: int = 10 # Valeur par défaut basée sur ton JSON

class DigitalizationItem(BaseModel):
    instrument: str
    fichier: str

class PartitionMongoBase(BaseModel):
    titre: str
    compositeur: str | None = None
    nomenclature: list[NomenclatureItem] | None = Field(default_factory=list)
    prestation: list[str] | None = Field(default_factory=list)
    date_distribution: str | None = None
    rendue: bool = False
    numero_archive: int | None = None
    audios: list[str] | None = Field(default_factory=list)
    # Pydantic supporte les caractères accentués, mais on reste vigilant
    numérisation: list[DigitalizationItem] | None = Field(default_factory=list)
    
    # Le lien vers SQL (injecté par la synchro)
    hbm_uuid: str | uuid.UUID | None = None 

class PartitionMongoCreate(PartitionMongoBase):
    pass

class PartitionMongoID(PartitionMongoBase):
    id: PyObjectId | None = Field(default=None, alias="_id")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AuthorResponse(BaseModel):
    """Utilisé pour afficher l'auteur et son rôle spécifique dans une partition"""
    identite: str | None = None # Champ désormais en base SQL
    role: str # Provient de la table d'association

    model_config = ConfigDict(from_attributes=True)

class SQLPartDetails(BaseModel):
    """Structure exacte de la clé 'catalogue_sql'"""
    titre: str
    ref_editeur: str | None = None
    numerisation: bool | None = None 
    hbm_uuid: uuid.UUID | str

class FullPartitionDetailsResponse(BaseModel):
    """
    C'est ici que la magie opère : on compose avec les schémas existants.
    SQLPartDetails est remplacé par l'utilisation directe de PartitionID et PartitionHbmID.
    """
    catalogue: PartitionID #
    inventaire: PartitionHbmID #
    auteurs: list[AuthorResponse] = []
    technique: PartitionMongoID | None = None

    model_config = ConfigDict(from_attributes=True)