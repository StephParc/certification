# regles_substitution.py
"""
API Router for Instrument Substitution Rules (MongoDB).

This module manages the business rules for instrument replacements within 
the orchestra. It allows administrators to define which instruments can 
substitute others based on musical family or specific technical criteria.

Security:
    - Default: 'read_only' scope required for retrieving rules.
    - Administrative: 'full_admin' scope required for creating or deleting rules.
"""
from fastapi import APIRouter, HTTPException, Depends, Security
from bson import ObjectId
from E4.harmonie.BDD.crud_mongo import get_one_document, get_many_documents, create_one_document, update_one_document, delete_one_document
from E4.harmonie.BDD.schemas_mongo import SubstitutionSchema, SubstitutionSchemaID
from E4.harmonie.BDD.auth import get_current_user

router = APIRouter(
    prefix="/substitutions", 
    tags=["Substitutions - Règles métier"],
    dependencies=[Security(get_current_user,scopes=["read_only"])]
)

COLLECTION = "COL_regles_substitution"

@router.post("/", response_model=str)
def create_substitution(data: SubstitutionSchema, current_user = Security(get_current_user, scopes=["full_admin"])):
    """
    Registers a new substitution rule.
    
    Requires 'full_admin' permissions. Validates that the current user has 
    the necessary authorization before writing to MongoDB.
    """
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    return create_one_document(COLLECTION, data.model_dump())

@router.get("/", response_model=list[SubstitutionSchemaID])
def get_substitutions_all():
    """Retrieves the complete list of substitution rules from MongoDB."""
    return get_many_documents(COLLECTION)

@router.get("/famille/{sous_famille}", response_model=list[SubstitutionSchemaID])
def get_substitutions_by_family(sous_famille: str):
    """
    Retrieves all rules associated with a specific instrument sub-family.
    
    Example: 'tubas' will return rules applicable to both Euphoniums and Tubas.
    The search is performed in lowercase for better compatibility.
    """
    query = {"sous_famille": sous_famille.lower()}
    results = get_many_documents(COLLECTION, query)
    if not results:
        raise HTTPException(status_code=404, detail=f"Aucune règle pour la famille {sous_famille}")
    return results

@router.delete("/{rule_id}")
def delete_substitution(rule_id: str, current_user = Security(get_current_user, scopes=["full_admin"])):
    """
    Removes a specific rule using its MongoDB ObjectId.
    
    Includes error handling for invalid ID formats to prevent API crashes.
    """
    if current_user.permissions != "full_admin":
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    
    try:
        success = delete_one_document(COLLECTION, {"_id": ObjectId(rule_id)})
        if not success:
            raise HTTPException(status_code=404, detail="Règle non trouvée")
        return {"status": "deleted"}
    except Exception:
        raise HTTPException(status_code=400, detail="ID invalide")