# instruments.py
"""
API Router for SQL Instrument Management.

This module provides endpoints for managing the relational instrument 
catalog. It handles standard CRUD operations for instruments within 
the PostgreSQL database, allowing for categorization by family and 
sub-family.

Security:
    - Default: 'read_only' scope required for listing instruments.
    - Administrative: 'full_admin' scope required for creating or deleting records.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Security
from sqlalchemy.orm import  Session

from E4.harmonie.BDD.crud import create_instrument,read_instrument_all,delete_instrument
from E4.harmonie.BDD.schemas import Instrument,InstrumentId
from E4.harmonie.BDD.auth import get_current_user
from E4.harmonie.BDD.database import get_session_sql

router = APIRouter(
    prefix="/instruments",
    tags=["Instruments"],
    dependencies=[Security(get_current_user,scopes=["read_only"])],
    responses={404: {"description":"Not found"}}
)

@router.get("/", response_model=list[InstrumentId])
def get_instrument_all(session:Session=Depends(get_session_sql)):
    """Retrieves the complete list of instruments from the relational database."""
    return read_instrument_all(session)
    
@router.post("/", response_model=InstrumentId)
def post_instrument(instrument: Instrument, session: Session = Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    """Registers a new instrument in the SQL catalog."""
    db_inst = create_instrument(session, nom=instrument.nom, famille=instrument.famille, sous_famille=instrument.sous_famille)
    session.commit()
    session.refresh(db_inst)
    return db_inst

@router.delete("/{instrument_id}")
def del_instrument(instrument_id: int, session: Session = Depends(get_session_sql),
            current_user = Security(get_current_user, scopes=["full_admin"])):
    """Removes an instrument record from the SQL database by its unique ID."""
    result = delete_instrument(session, instrument_id)
    if "Succès" in result:
        session.commit()
        return {"status": "success", "message": result}
    raise HTTPException(status_code=400, detail=result)
