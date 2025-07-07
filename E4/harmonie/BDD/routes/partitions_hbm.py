# partitions_hbm.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session
from crud import create_part_hbm_from_partition, read_partition_possessed_all, read_partition_possessed, read_partition_hbm_by_id, delete_partition_hbm
from schemas import PartitionHBM, PartitionHbmID
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/partitions_hbm",
    tags=["Partitions_hbm"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/", response_model=list[PartitionHbmID])
def get_partition_hbm_all(session:Session=Depends(get_session_sql)):
    return read_partition_possessed_all(session)

@router.get("/{partition_hbm_id}", response_model=list[PartitionHbmID])
def get_partition_hbm_by_id(part:PartitionHbmID, session:Session=Depends(get_session_sql)):
    partition = read_partition_hbm_by_id(session, part.partition_hbm_id)
    return partition

@router.post("/", response_model=PartitionHbmID)
def create_partition_hbm_from_partition(part:PartitionHBM, session:Session=Depends(get_session_sql)):
    part = create_part_hbm_from_partition(session, part.partition_id, part.distribution, part.rendue, part.archive, part.concert, part.defile, part.sonnerie)
    session.commit()
    session.refresh(part)
    return part

@router.delete("/{partition_hbm_id}")
def del_evenement(id:int, session:Session=Depends(get_session_sql)):
    result = delete_partition_hbm(session,id)
    session.commit()
    return result

# @router.put("/{event_id}")
# def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
#     result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
#     session.commit()
#     return result

# @router.patch("/{event_id}")
# def update_evenement(event:EventId, session:Session=Depends(get_session_sql)):
#     result = update_event(session, event.evenement_id, event.date_evenement, event.nom_evenement, event.lieu, event.type_evenement, event.affiche)
#     session.commit()
#     return result