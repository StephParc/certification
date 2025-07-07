# partitions.py
from fastapi import APIRouter, Depends, Security, Query
from sqlalchemy.orm import  Session
from crud import read_partition_by_id, read_partition_by_event_id, read_partition_by_event_date, read_partition_by_event_year, read_partition_by_id_complete, read_partition_by_composer, read_partition_by_arranger, read_partition_by_artist,read_partition_by_author, read_partition_by_creation_date, read_partition_by_grade, read_partition_by_genre, read_partition_all
from crud import create_part, delete_partition
from schemas import Partition, PartitionID, PartitionHbmID
from auth import get_current_user
from database import get_session_sql

router = APIRouter(
    prefix="/partitions",
    tags=["Partition"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description":"Not found"}},
)

@router.get("/{partition_id}", response_model=list[PartitionID])
def get_partition_by_id(id: int,session:Session=Depends(get_session_sql)):
    return read_partition_by_id(session, id)

# @router.get("/complete/{partition_id}", response_model=PartitionID)
# def get_partition_by_id_complete(id: int,session:Session=Depends(get_session_sql)):
#     return read_partition_by_id_complete(session, id)

# @router.get("/by_event_id/", response_model=list[list[PartitionHbmID]])
# def get_partition_by_event_id(id: int,session:Session=Depends(get_session_sql)):
#     return read_partition_by_event_id(session, id)

# @router.get("/by_event_date/", response_model=PartitionID)
# def get_partition_by_event_date(event_date:str=Query(description="Date au format YYYY-MM-DD"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_event_date(session, event_date)

# @router.get("/event_year/", response_model=PartitionID)
# def get_partition_by_event_year(event_year: int,session:Session=Depends(get_session_sql)):
#     return read_partition_by_event_year(session, event_year)

# @router.get("/by_composer/", response_model=PartitionID)
# def get_partition_by_composer(composer_id: int, name:str=Query(description="le nom contient:"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_composer(session, composer_id, name)

# @router.get("/by_arranger/", response_model=PartitionID)
# def get_partition_by_arranger(arranger_id: int, name:str=Query(description="le nom contient:"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_arranger(session, arranger_id, name)

# @router.get("/by_artist/", response_model=PartitionID)
# def get_partition_by_artist(artist_id: int, name:str=Query(description="le nom contient:"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_artist(session, artist_id, name)

# @router.get("/by_author/", response_model=PartitionID)
# def get_partition_by_author(author_id: int, name:str=Query(description="le nom contient:"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_author(session, author_id, name)

# informations partielles
@router.get("/by_creation_date/", response_model=list[PartitionID])
def get_partition_by_creation_date(creation_date,session:Session=Depends(get_session_sql)):
     return read_partition_by_creation_date(session, creation_date)


@router.get("/by_grade/")
def get_partition_by_grade(grade: float,session:Session=Depends(get_session_sql)):
    partitions = read_partition_by_grade(session, grade)
    response = []
    for partition in partitions:
        partition_dict = {
            "partition_id": partition.partition_id,
            "titre": partition.titre,
            "sous_titre": partition.sous_titre,
            "edition": partition.edition,
            "collection": partition.collection,
            "instrumentation": partition.instrumentation,
            "niveau": partition.niveau,
            "genre": partition.genre,
            "role": partition.role,
            "auteur": partition.auteur_nom_complet
        }
        response.append(partition_dict)

    return response
    
# @router.get("/by_genre/", response_model=list[PartitionID])
# def get_partition_by_genre(genre: str=Query(description="le genre contient:"),session:Session=Depends(get_session_sql)):
#     return read_partition_by_genre/(session, genre)

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

@router.get("/", response_model=list[PartitionID])
def get_partition_all(session:Session=Depends(get_session_sql)):
    return read_partition_all(session)