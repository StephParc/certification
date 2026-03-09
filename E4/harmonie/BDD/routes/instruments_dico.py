# instruments_dico.py
"""
API Router for the Instruments Dictionary (MongoDB).

This module provides endpoints for managing the master dictionary of 
musical instruments stored in MongoDB. It handles rich metadata for 
instruments and acts as a NoSQL complement to the relational instrument 
tables, using 'nom_sql' as the join key.

Security:
    - Default: 'read_only' scope required for all retrieval operations.
    - Administrative: 'full_admin' scope required for creating or deleting entries.
"""
from fastapi import APIRouter, HTTPException, Depends, Security
from E4.harmonie.BDD.crud_mongo import get_one_document, get_many_documents, create_one_document, update_one_document, delete_one_document
from E4.harmonie.BDD.schemas_mongo import InstrumentSchema, InstrumentSchemaID
from E4.harmonie.BDD.auth import get_current_user

router = APIRouter(
    prefix="/instruments-dico", 
    tags=["Instruments - dictionnaire"],
    dependencies=[Security(get_current_user,scopes=["read_only"])]
    )

COLLECTION = "COL_instruments"

@router.post("/", response_model=str)
def create_instrument(data: InstrumentSchema, current_user = Security(get_current_user, scopes=["full_admin"])):
    """Registers a new instrument entry in the MongoDB collection."""
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    return create_one_document(COLLECTION, data.model_dump())

@router.get("/", response_model=list[InstrumentSchemaID])
def get_instrument_all():
    """Retrieves all instrument documents with their MongoDB IDs."""
    return get_many_documents(COLLECTION)

@router.get("/{nom_sql}", response_model=InstrumentSchemaID)
def get_instrument_by_name(nom_sql: str):
    """Search for an instrument by its SQL name (join key with TB_instrument)."""
    doc = get_one_document(COLLECTION, {"nom_sql": nom_sql})
    if not doc:
        raise HTTPException(status_code=404, detail="Instrument non trouvé")
    return doc

@router.delete("/{nom_sql}")
def delete_instrument(nom_sql: str, current_user = Security(get_current_user, scopes=["full_admin"])):
    """Removes an instrument entry based on its unique SQL name reference."""
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    success = delete_one_document(COLLECTION, {"nom_sql": nom_sql})
    if not success:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"status": "deleted"}