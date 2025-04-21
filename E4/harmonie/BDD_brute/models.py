from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
import csv
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

# Ass_auteur_partition = Table(
#     'ass_auteur_partition', Base.metadata,
#     Column('auteur_id', Integer, ForeignKey('auteur.auteur_id'), primary_key=True),
#     Column('partition_id', Integer, ForeignKey('partition.partition_id'), primary_key=True),
#     Column('role', String, primary_key=True)
# )

# Ass_evenement_hbm = Table(
#     'ass_evenement_partition', Base.metadata,
#     Column('evenement_id', Integer, ForeignKey('evenement.evenement_id'), primary_key=True),
#     Column('hbm_id', Integer, ForeignKey('hbm.hbm_id'), primary_key=True)
# )

class Auteur(Base):
    __tablename__ = "auteur"

    auteur_id:  Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    identity:   Mapped[str] = mapped_column(String(), nullable=True)
    nom:        Mapped[str] = mapped_column(String(), nullable=True)
    prenom:     Mapped[str] = mapped_column(String(), nullable=True)
    ISNI:       Mapped[str] = mapped_column(String(), nullable=True)

    rel_partition_auteur: Mapped[List['Partition']]= relationship(
        'Partition', 
        secondary='ass_auteur_partition', 
        back_populates='rel_auteur_partition', 
        lazy='joined')
#     # rel_partition_auteur = relationship('Partition', secondary='ass_auteur_partition', back_populates='rel_auteur_partition')

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
#     rel_hbm_partition: Mapped[Optional['HBM']]= relationship(
#         'HBM', 
#         back_populates='hbm.hbm_id', 
#         uselist=False
#         # , cascade='all, delete-orphan'
#         )

class AssAuteurPartition(Base):
    __tablename__ = 'ass_auteur_partition'
    
    auteur_id:  Mapped[int] = mapped_column(ForeignKey('auteur.auteur_id'), primary_key=True)
    partition_id: Mapped[int] = mapped_column(ForeignKey('partition.partition_id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(), primary_key=True, nullable=False)

# class HBM(Base):
#     __tablename__ = "hbm"

#     hbm_id:         Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
#     partition_id:   Mapped[int]     = mapped_column(ForeignKey('partition.partition_id'), nullable=False, unique=True)
#     distribution:   Mapped[date]    = mapped_column(Date(), nullable=True)
#     rendue:         Mapped[bool]    = mapped_column(Boolean(), nullable=True)
#     archive:        Mapped[int]     = mapped_column(Integer(), nullable=True)
#     concert:        Mapped[bool]    = mapped_column(Boolean(), nullable=True)
#     defile:         Mapped[bool]    = mapped_column(Boolean(), nullable=True)
#     sonnerie:       Mapped[bool]    = mapped_column(Boolean(), nullable=True)

#     rel_partition_hbm: Mapped['Partition'] = relationship('Partition', back_populates='partition.partition_id')
#     rel_evenement_hbm: Mapped[List['Evenement']] = relationship(
#         'Evenement', 
#         secondary='ass_evenement_hbm', 
#         back_populates='rel_hbm_evenement',
#         lazy='joined')

class Evenement(Base):
    __tablename__ = "evenement"

    evenement_id:   Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    date_evenement: Mapped[date]    = mapped_column(Date(), nullable=False)
    nom_evenement:  Mapped[str]     = mapped_column(String(), nullable=False)
    lieu:           Mapped[str]     = mapped_column(String(), nullable=True)
    type_evenement: Mapped[str]     = mapped_column(String(), nullable=True)
    affiche:        Mapped[str]     = mapped_column(String(), nullable=True)

    # rel_hbm_evenement: Mapped[List['HBM']] = relationship(
    #     'HBM', 
    #     secondary='ass_evenement_hbm', 
    #     back_populates='rel_evenement_hbm',
    #     lazy='joined')

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("BDD créée")

############### INSERTION EN BDD ###########

session = SessionLocal()

# Insertion du csv évènements dans BDD
def insert_event_to_db(file_path):
    # Création d'une session
    # session = SessionLocal()
    print(file_path)

    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            print('csv_reader', csv_reader)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                event_exist = session.query(Evenement).filter_by(
                    date_evenement = datetime.strptime(row.get('date_event'), "%d-%m-%Y").date(),
                    nom_evenement = row.get('nom_event')).first()
                if event_exist is None:
                # Création d'un objet Evenement
                    evenement = Evenement(
                        date_evenement = datetime.strptime(row['date_event'], "%d-%m-%Y").date(),
                        nom_evenement = row['nom_event'],
                        lieu = row['lieu'],
                        type_evenement = row['type_event'],
                        affiche= row['affiche']
                    )
                    session.add(evenement)
                
                    # hbm=row['hbm'].lower() == 'true' if row['hbm'] else None            

        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

# Insertion du csv scraping dans BDD
def insert_auteur_to_db(file_path):
    # Création d'une session
    # session = SessionLocal()
    print(file_path)

    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                auteur_list = row.get('compositeur', None).upper().split(",")
                             
                for i in range(len(auteur_list)):
                    identity_test = auteur_list[i]
                    auteur_exist = session.query(Auteur).filter_by(identity = identity_test).first()
                    print('auteur_exist: ', auteur_exist)
                    if auteur_exist is None:
                        auteur = Auteur(                        
                            identity = identity_test
                        )
                        session.add(auteur)
                        session.flush()
                    # nom
                    # prenom
                    # ISNI
                             

        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

def insert_scrapy_to_db(file_path):
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                # déclarations des variables
                titre_test = row.get('titre').upper()
                sous_titre_test = row.get('sous_titre', None)
                edition_test = row.get('edition', None)
                collection_test = row.get('collection', None)
                instrumentation_test = row.get('instrumentation', None)
                niveau_test = float(row['niveau']) if row['niveau'] else None
                genre_test = row.get('genre', None)
                style_test = row.get('style', None)
                annee_sortie_test = int(row['annee_sortie']) if row['annee_sortie'] else None
                ISMN_test = row.get('ISMN', None)
                ref_editeur_test = row.get('ref_editeur', None)
                duree_test = row.get('duree', None)
                description_test = row.get('description', None)
                url_test = row.get('url', None)
                compositeur_list = row.get('compositeur', None).upper().split(",")
                artiste_list = row.get('artiste', None).upper().split(",")
                arrangeur_list = row.get('arrangeur', None).upper().split(",")

                # Vérification de l'existence de la partition en table
                existing_partition = session.query(Partition).filter_by(
                    titre = titre_test,
                    ref_editeur = ref_editeur_test
                    ).first()
                
                # Sélection ou création de l'enregistrement
                if existing_partition:
                    partition = existing_partition
                else:
                    partition = Partition(
                        titre           = titre_test,
                        sous_titre      = sous_titre_test,
                        edition         = edition_test,
                        collection      = collection_test,
                        instrumentation = instrumentation_test,
                        niveau          = niveau_test,
                        genre           = genre_test,
                        style           = style_test,
                        annee_sortie    = annee_sortie_test,
                        ISMN            = ISMN_test,
                        ref_editeur     = ref_editeur_test, 
                        duree           = duree_test,
                        description     = description_test,
                        url             = url_test
                   )
                    session.add(partition)
                    session.flush()  

                # Boucle sur les compositeurs 
                ## Vérification de l'existence du compositeur en table
                ## Sélection ou création de l'enregistrement
                if compositeur_list and compositeur_list!=[]:                
                    for i in range(len(compositeur_list)):
                        if compositeur_list[i]!='':
                            identity_test = compositeur_list[i]
                            existing_compositeur = session.query(Auteur).filter_by(identity = identity_test).first()
                            if existing_compositeur:
                                compositeur = existing_compositeur
                            else:
                                compositeur = Auteur(                        
                                    identity = identity_test
                                )
                                session.add(compositeur)
                                session.flush()
                        
                            # Vérification table d'association
                            existing_association = session.query(AssAuteurPartition).filter_by(
                                partition_id = partition.partition_id, 
                                auteur_id = compositeur.auteur_id,
                                role = 'compositeur').first()
                            
                            if not existing_association:
                                association = AssAuteurPartition(
                                    partition_id = partition.partition_id, 
                                    auteur_id = compositeur.auteur_id,
                                    role = 'compositeur'
                                )
                                session.add(association)
                                session.flush()

                # Boucle sur les artistes 
                ## Vérification de l'existence du artiste en table
                ## Sélection ou création de l'enregistrement
                if artiste_list and artiste_list!=[]:                
                    for i in range(len(artiste_list)):
                        if  artiste_list[i] != '':
                            identity_test = artiste_list[i]
                            existing_artiste = session.query(Auteur).filter_by(identity = identity_test).first()
                            if existing_artiste:
                                artiste = existing_artiste
                            else:
                                artiste = Auteur(                        
                                    identity = identity_test
                                )
                                session.add(artiste)
                                session.flush()
                            
                            # Vérification table d'association
                            existing_association = session.query(AssAuteurPartition).filter_by(
                                partition_id = partition.partition_id, 
                                auteur_id = artiste.auteur_id,
                                role = 'artiste').first()
                            
                            if not existing_association:
                                association = AssAuteurPartition(
                                    partition_id = partition.partition_id, 
                                    auteur_id = artiste.auteur_id,
                                    role = 'artiste'
                                )
                                session.add(association)
                                session.flush()

                # Boucle sur les arrangeurs 
                ## Vérification de l'existence du arrangeur en table
                ## Sélection ou création de l'enregistrement
                if arrangeur_list and arrangeur_list!=[]:                
                    for i in range(len(arrangeur_list)):
                        if arrangeur_list[i]!= '':
                            identity_test = arrangeur_list[i]
                            existing_arrangeur = session.query(Auteur).filter_by(identity = identity_test).first()
                            if existing_arrangeur:
                                arrangeur = existing_arrangeur
                            else:
                                arrangeur = Auteur(                        
                                    identity = identity_test
                                )
                                session.add(arrangeur)
                                session.flush()
                            
                            # Vérification table d'association
                            existing_association = session.query(AssAuteurPartition).filter_by(
                                partition_id = partition.partition_id, 
                                auteur_id = arrangeur.auteur_id,
                                role = 'arrangeur').first()
                            
                            if not existing_association:
                                association = AssAuteurPartition(
                                    partition_id = partition.partition_id, 
                                    auteur_id = arrangeur.auteur_id,
                                    role = 'arrangeur'
                                )
                                session.add(association)
                                session.flush()
                             

        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

# Chemin vers le fichier CSV
event_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/sources/events.csv"
scrapy_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/nouveau.csv"

# Importation des données CSV dans la base de données
insert_event_to_db(event_path)
# insert_auteur_to_db(scrapy_path)
insert_scrapy_to_db(scrapy_path)

