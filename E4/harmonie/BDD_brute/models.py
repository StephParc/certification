from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, DeclarativeBase
from datetime import date, datetime
import csv
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__),'.env')
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

metadata = MetaData()

class Auteur(Base):
    __tablename__ = "auteur"

    auteur_id:  Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    identity:   Mapped[str] = mapped_column(String(), nullable=True)
    nom:        Mapped[str] = mapped_column(String(), nullable=True)
    prenom:     Mapped[str] = mapped_column(String(), nullable=True)
    INSI:       Mapped[str] = mapped_column(String(), nullable=True)

    rel_partition_auteur: Mapped[List['Partition']]= relationship(
        'Partition', 
        secondary='ass_auteur_partition', 
        back_populates='rel_auteur_partition', 
        lazy='joined')

class Partition(Base):
    __tablename__ = "partition"

    partition_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
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
    hbm:            Mapped[bool]    = mapped_column(Boolean(), nullable=True)     

    rel_auteur_partition: Mapped[List['Auteur']] = relationship(
        'Auteur', 
        secondary='ass_auteur_partition', 
        back_populates='rel_partition_auteur',
        lazy='joined')
    rel_hbm_partition: Mapped[Optional['HBM']]= relationship(
        'HBM', 
        back_populates='rel_partition_hbm', 
        uselist=False
        # , cascade='all, delete-orphan'
        )

class AssAuteurPartition(Base):
    __tablename__ = 'ass_auteur_partition'
    
    auteur_id:  Mapped[int] = mapped_column(ForeignKey('auteur.auteur_id'), primary_key=True)
    partition_id: Mapped[int] = mapped_column(ForeignKey('partition.partition_id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(), primary_key=True, nullable=False)

class HBM(Base):
    __tablename__ = "hbm"

    hbm_id:         Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    partition_id:   Mapped[int]     = mapped_column(ForeignKey('partition.partition_id'), nullable=False, unique=True)
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
        secondary='ass_evenement_hbm', 
        back_populates='rel_hbm_evenement',
        lazy='joined')

class Evenement(Base):
    __tablename__ = "evenement"

    evenement_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    date_evenement: Mapped[date]    = mapped_column(Date(), nullable=False)
    nom_evenement:  Mapped[str]     = mapped_column(String(), nullable=False)
    lieu:           Mapped[str]     = mapped_column(String(), nullable=True)
    type_evenement: Mapped[str]     = mapped_column(String(), nullable=True)
    affiche:        Mapped[str]     = mapped_column(String(), nullable=True)

    rel_hbm_evenement: Mapped[List['HBM']] = relationship(
        'HBM', 
        secondary='ass_evenement_hbm', 
        back_populates='rel_evenement_hbm',
        lazy='joined')

class AssEvenementHbm(Base):
    __tablename__ = 'ass_evenement_hbm'

    evenement_id:   Mapped[int] = mapped_column(ForeignKey('evenement.evenement_id'), primary_key=True)
    hbm_id:         Mapped[int] = mapped_column(ForeignKey('hbm.hbm_id'), primary_key=True)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("BDD créée")
