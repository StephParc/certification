from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
# from .database import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
# from .config import DATABASE_URL

DATABASE_URL = "sqlite+pysqlite:///musicshop.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



metadata = MetaData()

Ass_auteur_partition = Table(
    'ass_auteur_partition', Base.metadata,
    Column('auteur_id', Integer, ForeignKey('auteur.auteur_id'), primary_key=True),
    Column('partition_id', Integer, ForeignKey('partition.partition_id'), primary_key=True),
    Column('role', String, primary_key=True)
)

Ass_evenement_hbm = Table(
    'ass_evenement_partition', Base.metadata,
    Column('evenement_id', Integer, ForeignKey('evenement.evenement_id'), primary_key=True),
    Column('hbm_id', Integer, ForeignKey('hbm.hbm_id'), primary_key=True)
)

class Auteur(Base):
    __tablename__ = "auteur"

    auteur_id:  Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    identity:   Mapped[str]
    nom:        Mapped[str]
    prenom:     Mapped[str]
    ISNI:       Mapped[str]

    rel_partition_auteur = relationship('Partition', secondary='ass_auteur_partition', back_populates='rel_auteur_partition')

class Partition(Base):
    __tablename__ = "partition"

    partition_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    titre:          Mapped[str]     
    sous_titre:     Mapped[str]     
    edition:        Mapped[str]     
    collection:     Mapped[str]     
    instrumentation:Mapped[str]     
    niveau:         Mapped[float]   = mapped_column(Float())
    genre:          Mapped[str]     
    style:          Mapped[str]     
    annee_sortie:   Mapped[int]     
    partie_euro:    Mapped[bool]    = mapped_column(Boolean())
    ISMN:           Mapped[str]     
    ref_editeur:    Mapped[str]     
    duree:          Mapped[str]     
    description:    Mapped[str]     
    url:            Mapped[str]
    hbm:            Mapped[bool]    = mapped_column(Boolean())     

    rel_auteur_partition = relationship('Auteur', secondary='ass_auteur_partition', back_populates='rel_partition_auteur')
    rel_hbm_partition = relationship('HBM', back_populates='hbm.hbm_id')

class HBM(Base):
    __tablename__ = "hbm"

    hbm_id:         Mapped[int]     = mapped_column(ForeignKey('partition.partition_id'), primary_key=True)
    distribution:   Mapped[str]     = mapped_column(Date())
    rendue:         Mapped[bool]    = mapped_column(Boolean())
    archive:        Mapped[int]
    concert:        Mapped[bool]    = mapped_column(Boolean())
    defile:         Mapped[bool]    = mapped_column(Boolean())
    sonnerie:       Mapped[bool]    = mapped_column(Boolean())

    rel_partition_hbm = relationship('Partition', back_populates='partition.partition_id')
    rel_evenement_hbm = relationship('Evenement', secondary='ass_evenement_hbm', back_populates='rel_hbm_evenement')

class Evenement(Base):
    __tablename__ = "evenement"

    evenement_id:   Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_evenement: Mapped[str] = mapped_column(Date())
    nom_evenement:  Mapped[str]
    lieu:           Mapped[str]
    type_evenement: Mapped[str]
    affiche:        Mapped[str]

    rel_hbm_evenement = relationship('HBM', secondary='ass_evenement_hbm', back_populates='rel_evenement_hbm')

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("BDD créée")



