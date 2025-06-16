# from models import Auteur, Partition, HBM, Evenement
from models import Auteur, AssAuteurPartition, Partition, PartitionHBM, AssEvenementHbm, Evenement, SessionLocal
from datetime import date, datetime
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship, noload
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
from sqlalchemy import select, update, delete, func, distinct, and_, or_, text
import csv

# ******** CREATE / POST ********
def create_event(session, date_evenement, nom_evenement, lieu=None, type_evenement=None, affiche=None):
    # Définition des variables de la requête pour vérifier l'existence
    date_evenement_test = date_evenement
    nom_evenement_test = nom_evenement
    lieu_test = lieu
    type_evenement_test = type_evenement
    affiche_test = affiche

    # Requête de vérification d"existence
    event_exist = session.query(Evenement).filter_by(
                    date_evenement = date_evenement_test,
                    nom_evenement = nom_evenement_test).first()
    
    # Création d'un nouvel Evenement
    if event_exist is None:
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
    # Définition des variables de la requête pour vérifier l'existence
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

    # Requête de vérification d"existence
    existing_partition = session.query(Partition).filter_by(
                    titre = titre_test,
                    ref_editeur = ref_editeur_test
                    ).first()
                
    # Sélection ou création de la partition
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

def create_auteur(session, nom=None, prenom=None, pays=None, IPI=None, ISNI=None):
    # Définition des variables de la requête pour vérifier l'existence
    nom_test = nom
    prenom_test = prenom
    pays_test = pays
    IPI_test = IPI
    ISNI_test = ISNI

    # Requête de vérification d"existence
    existing_auteur = session.query(Auteur).filter_by(
                    nom = nom_test,
                    prenom = prenom_test,
                    pays = pays_test,
                    IPI = IPI_test,
                    ISNI = ISNI_test).first()
    
    # Sélection ou création de l'auteur
    if existing_auteur :
        auteur = existing_auteur
    else:
        auteur = Auteur(
                nom = nom_test,
                prenom = prenom_test,
                pays = pays_test,
                IPI = IPI_test,
                ISNI = ISNI_test
                )
        session.add(auteur)
        session.flush()
    return auteur

def create_asso_auteur_partition(session, partition_id, auteur_id, role):
    # Définition des variables de la requête pour vérifier l'existence
    partition_id_test = partition_id
    auteur_id_test = auteur_id 
    role_test = role  

    # Requête de vérification d"existence
    existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id_test,
                auteur_id = auteur_id_test,
                role = role_test
                ).first()
    
    # Création de l'association auteur/partition
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
    # Définition des variables de la requête pour vérifier l'existence
    partition_id_test = partition_id
    distribution_test = distribution
    rendue_test = rendue
    archive_test = archive
    concert_test = concert
    defile_test = defile
    sonnerie_test = sonnerie

    existing_hbm = session.query(PartitionHBM).filter_by(partition_id=partition_id_test)

    if existing_hbm is None:
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


######## A FAIRE OU PAS (procédure création par étapes: partition, auteur(s), asso, partition_hbm) ########
# def create_hbm_from_scratch(session, partition_id, distribution=None, rendue=None, 
#                archive=None, concert=True, defile=False, sonnerie=False):
#     partition_id_test = partition_id
#     distribution_test = distribution
#     rendue_test = rendue
#     archive_test = archive
#     concert_test = concert
#     defile_test = defile
#     sonnerie_test = sonnerie

#     existing_hbm = session.query(HBM).filter_by(partition_id=partition_id_test)

#     if existing_hbm is None:
#         # raise error
#         pass
#     else:
#         hbm = HBM(
#             partition_id = partition_id_test,
#             distribution = distribution_test,
#             rendue = rendue_test,
#             archive = archive_test,
#             concert = concert_test,
#             defile = defile_test,
#             sonnerie = sonnerie_test)
#         session.add(hbm)
#         session.flush()

def create_asso_hbm_event(session, hbm_id, evenement_id):
    hbm_id_test = hbm_id
    event_id_test = evenement_id

    existing_asso = session.query(AssEvenementHbm).filter_by(
        partition_hbm_id=hbm_id_test, evenement_id=event_id_test).first()

    if existing_asso is None:
        existing_partition = session.query(PartitionHBM).filter_by(partition_hbm_id=hbm_id_test).first()
        if existing_partition:
            asso = AssEvenementHbm(
                partition_hbm_id = hbm_id_test,
                evenement_id = event_id_test
            )
            session.add(asso)
            session.flush()
            return asso

# ******** DELETE / DELETE ********
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
        existing_asso_hbm = session.query(PartitionHBM).filter_by(partition_id=partition_id).first()
        if existing_partition and not existing_asso_hbm:
            partition_id = existing_partition.partition_id
            session.delete(existing_partition)
            session.flush()

            stmt = delete(AssAuteurPartition).where(AssAuteurPartition.partition_id == partition_id)
            session.execute(stmt) 
            print("La partition a été supprimée")
            session.commit()
        else:
            print("suppression refusée")

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
        # Requête de vérification d"existence
        existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id,
                auteur_id = auteur_id,
                role = role
                ).first()
    
        if existing_asso:
        # Suppression de l'association
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
        # Requête de vérification d"existence
        existing_asso = session.query(AssEvenementHbm).filter_by(
                partition_hbm_id = partition_hbm_id,
                evenement_id = event_id
                ).first()
    
        if existing_asso:
        # Suppression de l'association
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


# ******** READ / GET ********
def read_event_by_id(session, event_id):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Evenement).options(noload('*')).where(Evenement.evenement_id==event_id)
    result = session.execute(stmt)
    evenement = result.first()
    session.close()
    return evenement

def read_event_by_date(session, event_date):
    # la date doit être au format YYYY-mm-dd
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Evenement).options(noload('*')).where(Evenement.date_evenement==event_date)
    result = session.execute(stmt)
    evenement = result.first()
    session.close()
    return evenement

def read_event_by_year(session, year):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Evenement).options(noload('*')).where(func.extract('year',Evenement.date_evenement)==year)
    result = session.execute(stmt)
    evenement = result.all()
    session.close()
    return evenement

def read_event_by_type(session, type):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Evenement).options(noload('*')).where(Evenement.type_evenement==type)
    result = session.execute(stmt)
    evenement = result.all()
    session.close()
    return evenement

def read_event_by_partition(session, partition_id):
    # liste les événements où une partition a été jouée
    stmt = select(Evenement).options(noload('*'))\
        .join(AssEvenementHbm)\
        .join(PartitionHBM)\
        .where(PartitionHBM.partition_hbm_id==partition_id)
    result = session.execute(stmt)
    evenement = result.all()
    session.close()
    return evenement

def read_partition_by_event_id(session, event_id):
    # liste le programme d'un événement (partitions jouées)
    stmt = select(PartitionHBM.partition_hbm_id, Partition.titre).options(noload('*'))\
        .join(AssEvenementHbm)\
        .join(Evenement)\
        .join(Partition)\
        .where(Evenement.evenement_id==event_id)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_event_date(session, event_date):
        # liste le programme d'un événement (partitions jouées)
    stmt = select(PartitionHBM.partition_hbm_id, Partition.titre).options(noload('*'))\
        .join(AssEvenementHbm)\
        .join(Evenement)\
        .join(Partition)\
        .where(Evenement.date_evenement==event_date)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_event_year(session, year):
        # liste le programme d'un événement (partitions jouées)
    stmt = select(PartitionHBM.partition_hbm_id, Partition.titre).options(noload('*'))\
        .join(AssEvenementHbm)\
        .join(Evenement)\
        .join(Partition)\
        .where(func.extract('year',Evenement.date_evenement)==year).distinct()
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_id(session, partition_id):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Partition).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id).add_columns(AssAuteurPartition.role)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur).where(Partition.partition_id==partition_id).distinct()
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_composer(session, composer_id, name):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur.prenom, Auteur.nom).where(and_(AssAuteurPartition.role=='compositeur', or_(Auteur.auteur_id==composer_id, Auteur.nom.ilike(name))))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_arranger(session, arranger_id, name):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur.prenom, Auteur.nom).where(and_(AssAuteurPartition.role=='arrangeur', or_(Auteur.auteur_id==arranger_id, Auteur.nom.ilike(name))))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_artist(session, artist_id, name):
    pass# l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur.prenom, Auteur.nom).where(and_(AssAuteurPartition.role=='artiste', or_(Auteur.auteur_id==artist_id, Auteur.nom.ilike(name))))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_author(session, author_id, name):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .where(or_(Auteur.auteur_id==author_id, Auteur.nom.ilike(name)))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_creation_date(session, creation_date):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Partition.partition_id, Partition.titre, Partition.annee_sortie).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .where(Partition.annee_sortie==creation_date)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_grade(session, grade):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Partition.partition_id, Partition.titre, Partition.niveau).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .where(Partition.niveau==grade)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_type(session, type):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    type=f"%{type}%"
    stmt = select(Partition.partition_id, Partition.titre, Partition.genre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .where(Partition.genre.ilike(type))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

# à vérifier
def read_partition_hbm_by_id(session, partition_id):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(PartitionHBM).options(noload('*'))\
        .join(Partition, PartitionHBM.partition_id==Partition.partition_id)\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id).add_columns(AssAuteurPartition.role)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur).where(PartitionHBM.partition_hbm_id==partition_id)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

# à vérifier
def read_partition_hbm_by_composer(session, composer_id, name):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(PartitionHBM.partition_hbm_id, Partition).options(noload('*'))\
        .join(Partition,PartitionHBM.partition_id==Partition.partition_id)\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur.prenom, Auteur.nom).where(and_(AssAuteurPartition.role=='compositeur', or_(Auteur.auteur_id==composer_id, Auteur.nom.ilike(name))))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_hbm_by_title(session, extrait):
    pass

def read_partition_possessed(session):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .join(PartitionHBM)\
        .add_columns(PartitionHBM.distribution, PartitionHBM.concert, PartitionHBM.defile, PartitionHBM.sonnerie)\
        .where(and_(PartitionHBM.distribution==None, or_(PartitionHBM.rendue==None, PartitionHBM.rendue==False)))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_possessed_by_type(session, type):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    if type == 'concert':
        stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .join(PartitionHBM)\
        .where(and_(PartitionHBM.distribution==None, or_(PartitionHBM.rendue==None, PartitionHBM.rendue==False), PartitionHBM.concert==True))
        result = session.execute(stmt)
        partition = result.all()
    elif type == 'défilé':
        stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .join(PartitionHBM)\
        .where(and_(PartitionHBM.distribution==None, or_(PartitionHBM.rendue==None, PartitionHBM.rendue==False), PartitionHBM.defile==True))
        result = session.execute(stmt)
        partition = result.all()
    elif type == 'sonnerie':
        stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .join(PartitionHBM)\
        .where(and_(PartitionHBM.distribution==None, or_(PartitionHBM.rendue==None, PartitionHBM.rendue==False), PartitionHBM.sonnerie==True))
        result = session.execute(stmt)
        partition = result.all()
    else:
        partition = []
    session.close()
    return partition

def read_auteur_by_id(session, auteur_id):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Auteur).options(noload('*')).where(Auteur.auteur_id==auteur_id)
    result = session.execute(stmt)
    auteur = result.first()
    session.close()
    return auteur

def read_auteur_by_name(session, nom):
    nom_partiel = f"%{nom}%"
    stmt = select(Auteur).options(noload('*')).where(Auteur.nom.ilike(nom_partiel))
    result = session.execute(stmt)
    auteur = result.all()
    session.close()
    return auteur

def read_auteur_by_role(session, role):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Auteur).options(noload('*'))\
        .join(AssAuteurPartition)\
        .where(AssAuteurPartition.role==role).distinct()
    result = session.execute(stmt)
    auteur = result.all()
    session.close()
    return auteur

# ******** UPDATE / PUT ********
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

def update_partition_hbm(session, partition_hbm_id):
    pass

def update_partition(session, partition_id):
    pass

def update_auteur(session, author_id):
    pass

# with open("database.py") as m:
#     code = m.read()
# exec(code)
session=SessionLocal()
print(read_event_by_id(session, 10))
# print(read_event_by_year(session, 2025))
# print(read_event_by_partition(session, 1))
# print(read_partition_by_event_id(session, 8))
# print(read_partition_by_event_date(session, '2025-04-27'))
# print(read_partition_by_event_year(session, 2025))
# print(read_auteur_by_id(session, 7))
# print(read_auteur_by_name(session, 'on'))
# print(read_auteur_by_role(session, 'arrangeur'))
# print(read_partition_by_id(session, 1))
# print(read_partition_by_author(session, 1, name='on'))
# print(read_partition_by_creation_date(session, None))
# print(read_partition_by_grade(session, None))
# print(read_partition_by_type(session, 'jazz'))
# print(read_partition_possessed(session))
# print(read_partition_hbm_by_id(session, 1))
# print(read_partition_hbm_by_composer(session, None, 'cahn'))
# print(read_partition_possessed_by_type(session, 'concert'))
# create_auteur(session, "Mozart", "Wolfgang")
# delete_auteur(session, 10)
# create_partition_hbm_from_partition(session, 3)
# session.commit()
# create_partition_hbm_from_partition(session, 4)
# session.commit()
# create_asso_hbm_event(session, 1,8)
# session.commit()
# create_asso_hbm_event(session, 2, 2)
# session.commit()
# delete_asso_partition_event(session, 4, 2)
# session.commit()
# delete_event(session, 2)
# session.commit()
session.close()