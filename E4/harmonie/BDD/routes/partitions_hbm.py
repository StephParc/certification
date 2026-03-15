# partitions_hbm.py
"""
API Router for SQL Partition Inventory.

This module manages the physical inventory of sheet music (TB_partition_hbm). 
It tracks distribution status, digitalization, and specific usage 
(concerts, parades) within the PostgreSQL database.

Security:
    - Default: 'read_only' scope required for viewing inventory.
    - Administrative: 'full_admin' scope required for inventory updates.
"""
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session

from E4.harmonie.BDD.crud import create_part_hbm_from_partition, read_partition_possessed_all, read_partition_possessed, read_partition_hbm_by_id, delete_partition_hbm
from E4.harmonie.BDD.schemas import PartitionHBM, PartitionHbmID
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.database import get_session_sql

router = APIRouter(
    prefix="/partitions_hbm",
    tags=["Partitions_hbm"],
    dependencies=[Security(get_current_user,scopes=["read_only"])],
    responses={404: {"description":"Not found"}}
)

@router.get("/", response_model=list[PartitionHbmID])
def get_partition_hbm_all(session:Session=Depends(get_session_sql)):
    """Retrieves the complete list of partitions in the physical inventory."""
    return read_partition_possessed_all(session)

@router.get("/{partition_hbm_id}", response_model=list[PartitionHbmID])
def get_partition_hbm_by_id(part:PartitionHbmID, session:Session=Depends(get_session_sql)):
    partition = read_partition_hbm_by_id(session, part.partition_hbm_id)
    return partition

@router.post("/", response_model=PartitionHbmID)
def create_partition_hbm_from_partition(part:PartitionHBM, session:Session=Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    """Registers a new physical partition record from a catalog reference."""
    part = create_part_hbm_from_partition(session, part.partition_id, part.distribution, part.rendue, part.numerisation, part.concert, part.defile, part.sonnerie)
    session.commit()
    session.refresh(part)
    return part

@router.delete("/{partition_hbm_id}")
def del_evenement(id:int, session:Session=Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    """Removes a partition from the physical inventory."""
    result = delete_partition_hbm(session,id)
    session.commit()
    return result
