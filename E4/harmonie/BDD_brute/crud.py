# from models import Auteur, Partition, HBM, Evenement
from models import Auteur, AssAuteurPartition, Partition, PartitionHBM, AssEvenementHbm, Evenement, SessionLocal
from datetime import date, datetime
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData, delete, update
import csv

# ******** CREATE ********
def create_event(session,
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
    return evenement          

def create_partition(session, titre, sous_titre=None, edition=None, collection=None,
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

def create_auteur(session, identity, nom=None, prenom=None, INSI=None):
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

# Version1
def create_asso_auteur_partition(session, partition_id, auteur_id, role):
    partition_id_test = partition_id
    auteur_id_test = auteur_id 
    role_test = role  

    existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id_test,
                auteur_id = auteur_id_test,
                role = role_test
                ).first()
    
    if existing_asso is None:
        # Création de l'association
        asso = AssAuteurPartition(
                partition_id = partition_id_test,
                auteur_id = auteur_id_test,
                role = role_test
                )
        session.add(asso)
        session.flush()
    # return asso

# def create_asso_auteur_partition(session, partition:Partition, auteur:Auteur, role:str):
#     partition_id_test = partition.partition_id
#     auteur_id_test = auteur.auteur_id 
#     role_test = role  

#     existing_asso = session.query(AssAuteurPartition).filter_by(
#                 partition_id = partition_id_test,
#                 auteur_id = auteur_id_test,
#                 role = role_test
#                 ).first()
    
#     if existing_asso is None:
#         # Création de l'association
#         asso = AssAuteurPartition(
#                 partition_id = partition_id_test,
#                 auteur_id = auteur_id_test,
#                 role = role_test
#                 )
#         session.add(asso)
#         session.flush()
#     return asso

def create_partition_hbm_from_partition(session, partition_id, distribution=None, rendue=None, 
               archive=None, concert=True, defile=False, sonnerie=False):
    partition_id_test = partition_id
    distribution_test = distribution
    rendue_test = rendue
    archive_test = archive
    concert_test = concert
    defile_test = defile
    sonnerie_test = sonnerie

    existing_hbm = session.query(PartitionHBM).filter_by(partition_id=partition_id_test)

    if existing_hbm is None:
        # raise error
        pass
    else:
        hbm = PartitionHBM(
            partition_id = partition_id_test,
            distribution = distribution_test,
            rendue = rendue_test,
            archive = archive_test,
            concert = concert_test,
            defile = defile_test,
            sonnerie = sonnerie_test)
        session.add(hbm)
        session.flush()
    return hbm


######## A FAIRE ########
def create_hbm_from_scratch(session, partition_id, distribution=None, rendue=None, 
               archive=None, concert=True, defile=False, sonnerie=False):
    partition_id_test = partition_id
    distribution_test = distribution
    rendue_test = rendue
    archive_test = archive
    concert_test = concert
    defile_test = defile
    sonnerie_test = sonnerie

    existing_hbm = session.query(HBM).filter_by(partition_id=partition_id_test)

    if existing_hbm is None:
        # raise error
        pass
    else:
        hbm = HBM(
            partition_id = partition_id_test,
            distribution = distribution_test,
            rendue = rendue_test,
            archive = archive_test,
            concert = concert_test,
            defile = defile_test,
            sonnerie = sonnerie_test)
        session.add(hbm)
        session.flush()

def create_asso_hbm_event(session, hbm_id, evenement_id):
    hbm_id_test = hbm_id
    event_id_test = evenement_id

    existing_asso = session.query(AssEvenementHbm).filter_by(
        hbm_id=hbm_id_test, evenement_id=event_id_test).first()

    if existing_asso is None:
        asso = AssEvenementHbm(
            partition_hbm_id = hbm_id_test,
            evenement_id = event_id_test
        )
        session.add(asso)
        session.flush()
    return asso

# ******** DELETE ********
def delete_event(session, event_id):
    try:
        existing_event = session.query(Evenement).filter_by(evenement_id=event_id).first()
        if existing_event:
            event_id = existing_event.evenement_id
            session.delete(existing_event)
            session.flush()

            stmt = delete(AssEvenementHbm).where(AssEvenementHbm.evenement_id == event_id)
            session.execute(stmt) 
            # existing_asso = session.query(AssEvenementHbm).filter_by(evenement_id=event_id).first()
            # session.delete(existing_asso)
            print("L'événement a été supprimé")
            session.commit()
        else:
            print("aucun événement trouvé")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

def delete_auteur(session, auteur_id):
    try:
        existing_auteur = session.query(Auteur).filter_by(auteur_id=auteur_id).first()
        if existing_auteur:
            auteur_id = existing_auteur.auteur_id
            session.delete(existing_auteur)
            session.flush()

            stmt = delete(AssAuteurPartition).where(AssAuteurPartition.auteur_id == auteur_id)
            session.execute(stmt) 
            print("L'auteur a été supprimé")
            session.commit()
        else:
            print("aucun auteur trouvé")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

def delete_partition(session, partition_id):
    try:
        existing_partition = session.query(Partition).filter_by(partition_id=partition_id).first()
        if existing_partition:
            partition_id = existing_partition.partition_id
            session.delete(existing_partition)
            session.flush()

            stmt = delete(AssAuteurPartition).where(AssAuteurPartition.partition_id == partition_id)
            session.execute(stmt) 
            print("La partition a été supprimée")
            session.commit()
        else:
            print("aucune partition trouvée")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

def delete_partition_hbm(session, partition_hbm_id):
    try:
        existing_partition = session.query(PartitionHBM).filter_by(partition_hbm_id=partition_hbm_id).first()
        if existing_partition:
            partition_id = existing_partition.partition_id
            partition_hbm_id = existing_partition.partition_hbm_id
            session.delete(existing_partition)
            session.commit()

            print("La partition a été supprimée")
        else:
            print("aucune partition trouvée")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

def delete_asso_auteur_partition(session, partition_id, auteur_id, role):
    try:
        existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id,
                auteur_id = auteur_id,
                role = role
                ).first()
    
        if existing_asso:
        # Création de l'association
            stmt = delete(AssAuteurPartition).where(
                AssAuteurPartition.partition_id == partition_id,
                AssAuteurPartition.auteur_id == auteur_id,
                AssAuteurPartition.role == role)
            session.execute(stmt) 
            print("L'association partition/auteur/role a été supprimée")
            session.commit()
        else:
            print("aucune correspondance trouvée")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

def delete_asso_partition_event(session, partition_hbm_id, event_id):
    try:
        existing_asso = session.query(AssEvenementHbm).filter_by(
                partition_hbm_id = partition_hbm_id,
                evenement_id = event_id
                ).first()
    
        if existing_asso:
        # Création de l'association
            stmt = delete(AssEvenementHbm).where(
                AssEvenementHbm.partition_hbm_id == partition_hbm_id,
                AssEvenementHbm.evenement_id == event_id)
            session.execute(stmt) 
            print("L'association partition/évènement a été supprimée")
            session.commit()
        else:
            print("aucune correspondance trouvée")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la suppression de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

# ******** UPDATE ********
# A FINIR
def update_event(session, event_id, date_evenement=None, nom_evenement=None, lieu=None, type_evenement=None, affiche=None):
    try:
        existing_event = session.query(Evenement).filter_by(evenement_id = event_id).first()

        if existing_event:    
            stmt = update(Evenement).where(
                Evenement.evenement_id == event_id).values(
                    date_evenement=date_evenement
                )
            session.execute(stmt) 
            print("L'évènement a été mis à jour")
            session.commit()
        else:
            print("aucune correspondance trouvée")

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de la mise à jour de l'enregistrement : {e}")
    finally:
        # Fermeture de la session
        session.close()

# ******** READ ********
def read_event_id(session):
    pass


session=SessionLocal()
# create_hbm_from_partition(session, 3)
# session.commit()
# create_hbm_from_partition(session, 4)
# session.commit()
# create_asso_hbm_event(session, 3, 2)
# session.commit()
# create_asso_hbm_event(session, 4, 2)
# session.commit()
delete_event(session, 2)
session.commit()