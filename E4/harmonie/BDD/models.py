# models.py . Contient les modèles SQLAlchemy des tables
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, text, ForeignKey, Table, MetaData
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, sessionmaker
from datetime import date, datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

from E4.harmonie.BDD.database import get_session_sql, get_engine

class Base(DeclarativeBase):
    pass

metadata = MetaData()

# AssAuteurPartition = Table('ass_auteur_partition', Base.metadata,
#     Column('auteur_id', Integer,  ForeignKey('auteur.auteur_id'), primary_key=True),
#     Column('partition_id', Integer, ForeignKey('partition.partition_id'), primary_key=True),
#     Column('role', String, primary_key=True, nullable=False))

# AssEvenementHbm = Table('ass_evenement_hbm', Base.metadata,
#     Column('evenement_id', Integer, ForeignKey('evenement.evenement_id', ondelete='CASCADE'), primary_key=True),
#     Column('partition_hbm_id', Integer, ForeignKey('partition_hbm.partition_hbm_id', ondelete='CASCADE'), primary_key=True))


class Auteur(Base):
    __tablename__ = "TB_auteur"

    auteur_id:  Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # identity:   Mapped[str] = mapped_column(String(), nullable=True)
    nom:        Mapped[str] = mapped_column(String(), nullable=True)
    prenom:     Mapped[str] = mapped_column(String(), nullable=True)
    identite:   Mapped[str] = mapped_column(String(), nullable=True)
    pays:       Mapped[str] = mapped_column(String(), nullable=True)
    IPI:        Mapped[str] = mapped_column(String(), nullable=True)
    ISNI:       Mapped[str] = mapped_column(String(), nullable=True)

    rel_partition_auteur: Mapped[List['Partition']]= relationship(
        'Partition', 
        secondary='TB_ass_auteur_partition', 
        back_populates='rel_auteur_partition', 
        lazy='joined')

    def __repr__(self) -> str:
        return f"Auteur(auteur_id={self.auteur_id!r}, nom={self.nom!r}, prenom={self.prenom!r}, pays={self.pays!r}, IPI={self.IPI!r}, ISNI={self.ISNI!r})"

class Partition(Base):
    __tablename__ = "TB_partition"

    partition_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    partition_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, 
                                        server_default=text("uuid_generate_v4()"))
    titre:          Mapped[str]     = mapped_column(String(), nullable=False)
    sous_titre:     Mapped[str]     = mapped_column(String(), nullable=True)
    edition:        Mapped[str]     = mapped_column(String(), nullable=True)
    collection:     Mapped[str]     = mapped_column(String(), nullable=True)
    instrumentation:Mapped[str]     = mapped_column(String(), nullable=True)
    niveau:         Mapped[float]   = mapped_column(Float(), nullable=True)
    genre:          Mapped[str]     = mapped_column(String(), nullable=True)
    style:          Mapped[str]     = mapped_column(String(), nullable=True)
    annee_sortie:   Mapped[int]     = mapped_column(Integer(), nullable=True)
    ISMN:           Mapped[str]     = mapped_column(String(), nullable=True)
    ref_editeur:    Mapped[str]     = mapped_column(String(), nullable=True)
    duree:          Mapped[str]     = mapped_column(String(), nullable=True)
    description:    Mapped[str]     = mapped_column(String(), nullable=True)
    url:            Mapped[str]     = mapped_column(String(), nullable=True)
    # hbm:            Mapped[bool]    = mapped_column(Boolean(), nullable=True)     

    rel_auteur_partition: Mapped[List['Auteur']] = relationship(
        'Auteur', 
        secondary='TB_ass_auteur_partition', 
        back_populates='rel_partition_auteur',
        lazy='joined')
    rel_hbm_partition: Mapped[Optional['PartitionHBM']]= relationship(
        'PartitionHBM', 
        back_populates='rel_partition_hbm', 
        uselist=False
        # , cascade='all, delete-orphan'
        )
    
    def __repr__(self) -> str:
        return f"Partition(partition_id={self.partition_id!r}, titre={self.titre!r}, sous_titre={self.sous_titre!r}, \
edition={self.edition!r}, collection={self.collection!r}, instrumentation={self.instrumentation!r}, \
niveau={self.niveau!r}, genre={self.genre!r}, style={self.style!r}, \
annee_sortie={self.annee_sortie!r}, ISMN={self.ISMN!r}, ref_editeur={self.ref_editeur!r}, \
duree={self.duree!r}, description={self.description!r}, url={self.url!r})"

# Version1
class AssAuteurPartition(Base):
    __tablename__ = 'TB_ass_auteur_partition'
    
    auteur_id:  Mapped[int] = mapped_column(ForeignKey('TB_auteur.auteur_id'), primary_key=True)
    partition_id: Mapped[int] = mapped_column(ForeignKey('TB_partition.partition_id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(), primary_key=True, nullable=False)

    def __repr__(self):
        return f"AssAuteurPartition(auteur_id={self.auteur_id!r}, partition_id={self.partition_id!r}, role={self.role!r}"

class PartitionHBM(Base):
    __tablename__ = "TB_partition_hbm"

    partition_hbm_id:Mapped[int]    = mapped_column(primary_key=True, autoincrement=True)
    hbm_uuid: Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True),unique=True, nullable=False, 
                                        server_default=text("uuid_generate_v4()"))
    partition_id:   Mapped[int]     = mapped_column(ForeignKey('TB_partition.partition_id'), nullable=True, unique=True)
    distribution:   Mapped[date]    = mapped_column(Date(), nullable=True)
    rendue:         Mapped[bool]    = mapped_column(Boolean(), nullable=True)
    archive:        Mapped[int]     = mapped_column(Integer(), nullable=True)
    concert:        Mapped[bool]    = mapped_column(Boolean(), nullable=True)
    defile:         Mapped[bool]    = mapped_column(Boolean(), nullable=True)
    sonnerie:       Mapped[bool]    = mapped_column(Boolean(), nullable=True)

    rel_partition_hbm: Mapped['Partition'] = relationship(
        'Partition', 
        back_populates='rel_hbm_partition',
        lazy='joined')
    rel_evenement_hbm: Mapped[List['Evenement']] = relationship(
        'Evenement', 
        secondary='TB_ass_evenement_hbm', 
        back_populates='rel_hbm_evenement',
        lazy='joined')
    
    def __repr__(self):
        return f"PartitionHBM(partition_hbm_id={self.partition_hbm_id!r}, partition_id={self.partition_id!r}, \
distribution={self.distribution!r}, rendue={self.rendue!r}, archive={self.archive!r}, \
concert={self.concert!r}, defile={self.defile!r}, sonnerie={self.sonnerie!r})"

class Evenement(Base):
    __tablename__ = "TB_evenement"

    evenement_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    date_evenement: Mapped[date]    = mapped_column(Date(), nullable=False)
    nom_evenement:  Mapped[str]     = mapped_column(String(), nullable=False)
    lieu:           Mapped[str]     = mapped_column(String(), nullable=True)
    type_evenement: Mapped[str]     = mapped_column(String(), nullable=True)
    affiche:        Mapped[str]     = mapped_column(String(), nullable=True)

    rel_hbm_evenement: Mapped[List['PartitionHBM']] = relationship(
        'PartitionHBM', 
        secondary='TB_ass_evenement_hbm', 
        back_populates='rel_evenement_hbm',
        lazy='joined')
    
    def __repr__(self):
        return f"Evenement(evenement_id={self.evenement_id!r}, date_evenement={self.date_evenement}, nom_evenement={self.nom_evenement!r}, lieu={self.lieu!r}, type_evenement={self.type_evenement!r}, affiche={self.affiche!r})"

# Version1
class AssEvenementHbm(Base):
    __tablename__ = 'TB_ass_evenement_hbm'

    evenement_id:       Mapped[int] = mapped_column(ForeignKey('TB_evenement.evenement_id', ondelete='CASCADE'), primary_key=True)
    partition_hbm_id:   Mapped[int] = mapped_column(ForeignKey('TB_partition_hbm.partition_hbm_id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return super().__repr__()
    
    def __repr__(self) -> str:
        return f"AssEvenement(evenement_id={self.evenement_id!r}, partition_hbm_id={self.partition_hbm_id!r})"
    
class Instrument(Base):
    __tablename__ = "TB_instrument"

    instrument_id:  Mapped[int]         = mapped_column(primary_key=True, autoincrement=True)
    instrument_uuid: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, 
                                            server_default=text("uuid_generate_v4()"))
    nom:            Mapped[str]         = mapped_column(String(100), nullable=False, unique=True)
    famille:        Mapped[str]         = mapped_column(String(50), nullable=True)
    sous_famille:   Mapped[str]         = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"Instrument(id={self.instrument_id}, nom={self.nom})"

class User(Base):
    __tablename__ = "TB_utilisateur"

    user_id:            Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_uuid:    Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),unique=True,nullable=False, 
                                        server_default=text("uuid_generate_v4()"))
    pseudo:             Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    fullname:           Mapped[str] = mapped_column(String(), nullable=True)
    hashed_password:    Mapped[str] = mapped_column(String(), nullable=False)
    email:              Mapped[str] = mapped_column(String(), nullable=True)
    permissions:        Mapped[str] = mapped_column(String(), nullable=True)
    last_connection:    Mapped[date]= mapped_column(Date(), nullable=True)

    def __repr__(self):
        return f"User(user_id={self.user_id!r}, username={self.pseudo}, fullname={self.fullname!r}, hashed_password={self.hashed_password!r}, email={self.email!r}, permissions={self.permissions!r})"


# if __name__ == "__main__":
#     engine = get_engine()
#     Base.metadata.create_all(bind=engine)
#     print("BDD créée")
