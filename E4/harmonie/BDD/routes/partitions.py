# partitions.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import  Session
from crud import create_part, read_partition_all, read_partition_by_id, delete_partition
from schemas import Partition, PartitionID
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/partitions",
    tags=["Partition"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/", response_model=list[PartitionID])
def get_partition_all(session:Session=Depends(get_session_sql)):
    return read_partition_all(session)

@router.get("/{partition_id}", response_model=PartitionID)
def get_partition_by_id(id: int,session:Session=Depends(get_session_sql)):
    return read_partition_by_id(session, id)

@router.post("/", response_model=Partition)
def create_partition(part:Partition, session:Session=Depends(get_session_sql)):
    titre = part.titre
    sous_titre = part.sous_titre
    edition = part.edition
    collection = part.collection
    instrumentation = part.instrumentation
    niveau = part.niveau
    genre = part.genre
    style = part.style
    annee_sortie = part.annee_sortie
    ISMN = part.ISMN
    ref_editeur = part.ref_editeur
    duree = part.duree
    description = part.description
    url = part.url  
    part=create_part(session, titre, sous_titre, edition, collection, instrumentation, niveau, genre, style, annee_sortie, ISMN, ref_editeur, duree, description, url)
    session.commit()
    session.refresh(part)
    return part

@router.delete("/{partition_id}")
def del_partition(id:int, session:Session=Depends(get_session_sql)):
    result = delete_partition(session,id)
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