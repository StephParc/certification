# instruments_dico.py
from fastapi import APIRouter, HTTPException, Depends
from E4.harmonie.BDD.crud_mongo import get_one_document, get_many_documents, create_one_document, update_one_document, delete_one_document
from E4.harmonie.BDD.schemas_mongo import InstrumentSchema, InstrumentSchemaID
from E4.harmonie.BDD.auth import get_current_user

router = APIRouter(
    prefix="/instruments-dico", 
    tags=["Instruments - dictionnaire"]
    )

COLLECTION = "COL_instruments"

# router = APIRouter(
#     prefix="/instruments",
#     tags=["Instruments"],
#     dependencies=[Depends(get_current_user)],
#     responses={404: {"description":"Not found"}},
# )

@router.post("/", response_model=str)
def create_instrument(data: InstrumentSchema, current_user = Depends(get_current_user)):
    """Création sans ID dans le corps de la requête."""
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    return create_one_document(COLLECTION, data.model_dump())

@router.get("/", response_model=list[InstrumentSchemaID])
def get_instrument_all():
    """Récupération de tous les instruments avec leurs IDs Mongo."""
    return get_many_documents(COLLECTION)

@router.get("/{nom_sql}", response_model=InstrumentSchemaID)
def get_instrument_by_name(nom_sql: str):
    """Recherche par nom_sql (clé de jointure avec TB_instrument)."""
    doc = get_one_document(COLLECTION, {"nom_sql": nom_sql})
    if not doc:
        raise HTTPException(status_code=404, detail="Instrument non trouvé")
    return doc

@router.delete("/{nom_sql}")
def delete_instrument(nom_sql: str, current_user = Depends(get_current_user)):
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    success = delete_one_document(COLLECTION, {"nom_sql": nom_sql})
    if not success:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"status": "deleted"}