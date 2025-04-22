# from models import Auteur, Partition, HBM, Evenement
from models import Auteur, Partition, AssAuteurPartition, Evenement
from datetime import date, datetime
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
import csv


def insert_event(session,
    date_evenement,
    nom_evenement,
    lieu=None,
    type_evenement=None,
    affiche=None):

    date_evenement_test = date_evenement
    nom_evenement_test = nom_evenement
    lieu_test = lieu
    type_evenement_test = type_evenement
    affiche_test = affiche

    event_exist = session.query(Evenement).filter_by(
                    date_evenement = date_evenement_test,
                    nom_evenement = nom_evenement_test).first()
    if event_exist is None:
    # Création d'un objet Evenement
        evenement = Evenement(
                date_evenement = date_evenement_test,
                nom_evenement = nom_evenement_test,
                lieu = lieu_test,
                type_evenement = type_evenement_test,
                affiche= affiche_test
                )
        session.add(evenement)
        session.flush()          

def insert_partition(session, titre, sous_titre=None, edition=None, collection=None,
                instrumentation=None, niveau=None, genre=None, style=None, annee_sortie=None,
                ISMN=None, ref_editeur=None, duree=None, description=None, url=None):
    titre_test           = titre
    sous_titre_test      = sous_titre
    edition_test         = edition
    collection_test      = collection
    instrumentation_test = instrumentation
    niveau_test          = niveau
    genre_test           = genre
    style_test           = style
    annee_sortie_test    = annee_sortie
    ISMN_test            = ISMN
    ref_editeur_test     = ref_editeur 
    duree_test           = duree
    description_test     = description
    url_test             = url

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
    return partition

def insert_auteur(session, identity, nom=None, prenom=None, INSI=None):
    identity_test = identity
    nom_test = nom
    prenom_test = prenom
    INSI_test = INSI

    existing_auteur = session.query(Auteur).filter_by(
                    identity = identity_test).first()
    
    if existing_auteur :
        auteur = existing_auteur
    else:
    # Création d'un objet Partition
        auteur = Auteur(
                identity = identity_test,
                nom = nom_test,
                prenom = prenom_test,
                INSI = INSI_test
                )
        session.add(auteur)
        session.flush()
    return auteur

def insert_asso_auteur_partition(session, partition_id, auteur_id, role):
    partition_id_test = partition_id
    auteur_id_test = auteur_id 
    role_test = role  

    existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id_test,
                auteur_id = auteur_id_test,
                role = role_test
                ).first()
    
    if existing_asso is None:
        # Création d'un objet Partition
        asso = AssAuteurPartition(
                partition_id = partition_id_test,
                auteur_id = auteur_id_test,
                role = role_test
                )
        session.add(asso)
        session.flush()