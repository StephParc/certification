# partitions_details.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from E4.harmonie.BDD.crud_mongo import get_partition_by_uuid
from E4.harmonie.BDD.database import get_session_sql
from E4.harmonie.BDD.schemas_mongo import FullPartitionDetailsResponse
from E4.harmonie.BDD.models import PartitionHBM, AssAuteurPartition, Auteur

router = APIRouter(
    prefix="/partitions-details", 
    tags=["Partitions - Vue Hybride"]
    )

@router.get("/{hbm_uuid}", response_model=FullPartitionDetailsResponse)
def get_full_partition_details(hbm_uuid: str, session: Session = Depends(get_session_sql)):
    """
    Fusionne les données SQL (Inventaire/Catalogue) et MongoDB (Nomenclature/Fichiers).
    """
    hbm_entry = session.query(PartitionHBM).filter(PartitionHBM.hbm_uuid == hbm_uuid).first()
    if not hbm_entry:
        raise HTTPException(status_code=404, detail="UUID SQL introuvable")
    
    auteurs_query = (
        session.query(Auteur.identite, AssAuteurPartition.role)
        .join(AssAuteurPartition, Auteur.auteur_id == AssAuteurPartition.auteur_id)
        .filter(AssAuteurPartition.partition_id == hbm_entry.partition_id)
        .all()
    )

    mongo_data = get_partition_by_uuid(hbm_uuid)

    return {
        "catalogue": hbm_entry.rel_partition_hbm, 
        "inventaire": hbm_entry,                
        "auteurs": auteurs_query,               
        "technique": mongo_data
    }