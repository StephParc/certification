# associations.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session
from crud import create_asso_auteur_partition,read_asso_auteur_partition_all, delete_asso_auteur_partition
from crud import create_asso_hbm_event, read_asso_partition_event_all, delete_asso_partition_event
from schemas import Role, AuteurPartition, AssoAuteurPartition, PartitionEvent
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/associations",
    tags=["Auteur/Partition - Partition/Evénement"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/auteur_partition/all", response_model=list[AssoAuteurPartition])
def get_ass_auteur_partition_all(session:Session=Depends(get_session_sql)):
    return read_asso_auteur_partition_all(session)

@router.post("/auteur_partition")
def create_ass_auteur_partition(asso:AuteurPartition, role:Role, session:Session=Depends(get_session_sql)):
    association = create_asso_auteur_partition(session,asso.partition_id, asso.auteur_id, role)
    session.commit()
    session.refresh(association)
    return association

@router.delete("/auteur_partition")
def del_ass_auteur_partition(auteur_id:int, partition_id: int, role: Role, session:Session=Depends(get_session_sql)):
    result = delete_asso_auteur_partition(session, partition_id, auteur_id, role)
    session.commit()
    return result

@router.get("/partition_evenement", response_model=list[PartitionEvent])
def get_ass_partition_evenement_all(session:Session=Depends(get_session_sql)):
    return read_asso_partition_event_all(session)

@router.post("/partition_evenement", response_model=PartitionEvent)
def create_ass_partition_evenement(asso:PartitionEvent, session:Session=Depends(get_session_sql)):
    association = create_asso_hbm_event(session,asso.partition_hbm_id, asso.evenement_id)
    session.commit()
    session.refresh(association)
    return association

@router.delete("/partition_evenement")
def del_ass_partition_evenement(partition_hbm_id:int, event_id: int, session:Session=Depends(get_session_sql)):
    result = delete_asso_partition_event(session, partition_hbm_id, event_id)
    session.commit()
    return result