# crud.py
from sqlalchemy.orm import noload
from sqlalchemy import select, update, delete, func, distinct, and_, or_, text

from E4.harmonie.BDD.models import Auteur, AssAuteurPartition, Partition, PartitionHBM, AssEvenementHbm, Evenement, User, Instrument
from E4.harmonie.BDD.schemas import UserPublic, UserAdmin, UserPass
from E4.harmonie.BDD.auth import get_password_hash
from E4.harmonie.BDD.database import get_session_sql, sql_connect
from E4.harmonie.BDD.api_externe import get_api_externe
from utils.logger_config import setup_logger, trace_action
from utils.utils_functions import normalize_name

## pour exécuter les fonctions directemet de ce script, il faut ouvrir la session ainsi et la fermer à la fin:
# Session = sql_connect()
# session = Session()
## selon les opérations
# session.commit()
# session.close()

# ******** CREATE / POST ********
    
def create_event(session, date_evenement, nom_evenement, lieu=None, type_evenement=None, affiche=None):
    # date_evenement = datetime.strptime(date_evenement, "%d-%m-%Y").date()
    # 1. Vérif simple
    existing = session.query(Evenement).filter_by(
        date_evenement=date_evenement, 
        nom_evenement=nom_evenement
    ).first()
    
    if existing:
        return existing
    
    # 2. Création manuelle (on écrit chaque champ)
    evenement = Evenement(
        date_evenement=date_evenement,
        nom_evenement=nom_evenement,
        lieu=lieu,
        type_evenement=type_evenement,
        affiche=affiche
    )
    session.add(evenement)
    session.flush()
    return evenement          

def create_part(session, titre, sous_titre=None, edition=None, collection=None,
                instrumentation=None, niveau=None, genre=None, style=None, annee_sortie=None,
                ISMN=None, ref_editeur=None, duree=None, description=None, url=None):

    titre_clean = titre.upper() if titre else ""
    # Requête de vérification d"existence
    existing_partition = session.query(Partition).filter_by(
                    titre = titre_clean,
                    ref_editeur = ref_editeur
                    ).first()
                
    # Sélection ou création de la partition
    if existing_partition:
        return existing_partition
    
    partition = Partition(
                titre           = titre_clean,
                sous_titre      = sous_titre,
                edition         = edition,
                collection      = collection,
                instrumentation = instrumentation,
                niveau          = niveau,
                genre           = genre,
                style           = style,
                annee_sortie    = annee_sortie,
                ISMN            = ISMN,
                ref_editeur     = ref_editeur, 
                duree           = duree,
                description     = description,
                url             = url)
    session.add(partition)
    session.flush()  
    return partition

def create_auteur(session, nom=None, prenom=None, identite=None, pays=None, IPI=None, ISNI=None):
    
    search_id = normalize_name(nom, prenom)
    search_id_inv = normalize_name(prenom, nom)

    existing_brut = session.query(Auteur).filter(
        or_(
            Auteur.identite == search_id,
            Auteur.identite == search_id_inv
            )
        ).first()
    if existing_brut:
        return existing_brut
    
    auteur_api = get_api_externe(search_id)

    if auteur_api:
        final_nom = auteur_api.get("Nom")
        final_prenom = auteur_api.get("Prénom")
        final_identite = normalize_name(final_nom, final_prenom)

        existing_clean = session.query(Auteur).filter_by(identite=final_identite).first()
        if existing_clean:
            return existing_clean

        final_pays = auteur_api.get("Pays")
        final_ipi = auteur_api.get("IPI")
        final_isni = auteur_api.get("ISNI")
    else:
        final_nom = nom
        final_prenom = prenom
        final_identite = normalize_name(nom=final_nom, prenom=final_prenom)
        final_pays = pays
        final_ipi = IPI
        final_isni = ISNI

    auteur = Auteur(
        nom=final_nom,
        prenom=final_prenom,
        identite=final_identite,
        pays=final_pays,
        IPI=final_ipi,
        ISNI=final_isni
    )

    session.add(auteur)
    session.flush()
    return auteur

def create_asso_auteur_partition(session, partition_id, auteur_id, role):
    # Requête de vérification d"existence
    existing_asso = session.query(AssAuteurPartition).filter_by(
                partition_id = partition_id,
                auteur_id = auteur_id,
                role = role
                ).first()
    
    if existing_asso:
        return existing_asso
    
    # Création de l'association auteur/partition

    asso = AssAuteurPartition(
            partition_id = partition_id,
            auteur_id = auteur_id,
            role = role
            )
    session.add(asso)
    session.flush()
    return asso


# A revoir
def create_part_hbm_from_partition(session, partition_id=None, distribution=None, rendue=None, 
                numerisation=None, concert=True, defile=False, sonnerie=False):
    if partition_id:
        existing_hbm = session.query(PartitionHBM).filter_by(partition_id=partition_id).first()
        if existing_hbm :
            return existing_hbm
        hbm = PartitionHBM(partition_id = partition_id,
                distribution = distribution,
                rendue = rendue,
                numerisation = numerisation,
                concert = concert,
                defile = defile,
                sonnerie = sonnerie)
    session.add(hbm)
    session.flush()
    return hbm


######## A FAIRE OU PAS (procédure création par étapes: partition, auteur(s), asso, partition_hbm) ########
# def create_hbm_from_scratch(session, partition_id, distribution=None, rendue=None, 
#                numerisation=None, concert=True, defile=False, sonnerie=False):
#     partition_id_test = partition_id
#     distribution_test = distribution
#     rendue_test = rendue
#     numerisation_test = numerisation
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
#             numerisation = numerisation_test,
#             concert = concert_test,
#             defile = defile_test,
#             sonnerie = sonnerie_test)
#         session.add(hbm)
#         session.flush()

def create_asso_hbm_event(session, hbm_id, evenement_id):
    existing_asso = session.query(AssEvenementHbm).filter_by(
        partition_hbm_id=hbm_id, evenement_id=evenement_id).first()

    if existing_asso is None:
        existing_partition = session.query(PartitionHBM).filter_by(partition_hbm_id=hbm_id).first()
        if existing_partition:
            asso = AssEvenementHbm(
                partition_hbm_id = hbm_id,
                evenement_id = evenement_id            )
            session.add(asso)
            session.flush()
            return asso

def create_user(session, pseudo, password, fullname=None, email=None):
    # Fonction de hachage du mot de passe
    hashed_password = get_password_hash(password)
    
    # Requête de vérification d"existence
    existing_user = session.query(User).filter_by(pseudo = pseudo).first()
    if existing_user:
        return "Cet utilisateur existe déjà"

    # Création d'un nouvel utilisateur
    user = User(
                pseudo = pseudo,
                fullname = fullname,
                email = email,
                hashed_password = hashed_password
    )
    
    session.add(user)
    session.flush()
    return user

def create_user_admin(session, pseudo, fullname, hashed_password, email, permissions):
    # 1. Vérification d'existence
    existing_user = session.query(User).filter_by(pseudo=pseudo).first()
    if existing_user:
        # Il vaut mieux retourner l'objet existant ou None plutôt qu'un message str
        # pour ne pas faire planter les scripts qui attendent un objet User
        return existing_user

    # 3. Création de l'utilisateur avec l'UUID généré par Postgres
    user = User(
        pseudo=pseudo, 
        fullname = fullname,
        email = email,
        hashed_password = hashed_password,
        permissions = permissions)

    session.add(user)
    session.flush() # Pour récupérer le user_uuid immédiatement si besoin
    return user

def create_instrument(session, nom, famille, sous_famille=None):
    existing_instrument = session.query(Instrument).filter_by(nom=nom).first()
    if existing_instrument:
        return existing_instrument
    
    instrument = Instrument(nom=nom, famille=famille, sous_famille=sous_famille)
    session.add(instrument)
    session.flush()
    return instrument

# ******** DELETE / DELETE ********
def delete_event(session, event_id):
    try:
        existing_event = session.query(Evenement).filter_by(evenement_id=event_id).first()
        if existing_event:
            target_id = existing_event.evenement_id
            stmt = delete(AssEvenementHbm).where(AssEvenementHbm.evenement_id == target_id)
            session.execute(stmt)
            session.delete(existing_event)
            session.flush()
            message = f"Succès : L'événement {target_id} a été supprimé."
        else:
            message = f"Échec : L'événement n'existe pas."

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'événement : {str(e)}"
    
    return message

def delete_auteur(session, auteur_id):
    try:
        existing_auteur = session.query(Auteur).filter_by(auteur_id=auteur_id).first()
        if existing_auteur:
            auteur_id = existing_auteur.auteur_id
            stmt = delete(AssAuteurPartition).where(AssAuteurPartition.auteur_id == auteur_id)
            session.execute(stmt) 
            session.delete(existing_auteur)                     
            session.flush()
            message = f"Succès : L'auteur {auteur_id} a été supprimé ainsi que ses associations"
        else:
            message = f"Échec : Aucun auteur trouvé avec l'ID {auteur_id}."

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'auteur: {str(e)}"

    return message

# A revoir
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
            message = "La partition a été supprimée"
            session.commit()
        else:
            message= "La partition n'existe pas"

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'enregistrement : {e}"
    finally:
        # Fermeture de la session
        session.close()
        return message

# A revoir
def delete_partition_hbm(session, partition_hbm_id):
    try:
        existing_partition = session.query(PartitionHBM).filter_by(partition_hbm_id=partition_hbm_id).first()
        if existing_partition:
            partition_id = existing_partition.partition_id
            partition_hbm_id = existing_partition.partition_hbm_id
            session.delete(existing_partition)
            session.commit()
            message = "La partition a été supprimée"
        else:
            message = "aucune partition trouvée"

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'enregistrement : {e}"
    finally:
        # Fermeture de la session
        session.close()
        return message

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
            session.flush()
            message = f"Succès : L'association pour la partition {partition_id} a été supprimée."
        else:
            message = f"Échec : Aucune correspondance trouvée pour cette association."

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'association : {str(e)}"

    return message

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
            session.flush()
            message = f"Succès : L'association entre la partition HBM {partition_hbm_id} et l'événement {event_id} a été supprimée."
        else:
            message = f"Échec : Aucune correspondance trouvée pour cette association."

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la suppression de l'association : {str(e)}"

    return message

def delete_user(session, user_id):
    try:
        existing_user = session.query(User).filter_by(user_id=user_id).first()
        if existing_user:
            u_id = existing_user.user_id
            session.delete(existing_user)
            session.flush()
            print(f"Succès : L'utilisateur {u_id} a été supprimé.")
            message = f"Succès : L'utilisateur {u_id} a été supprimé."
        else:
            print(f"Échec : L'utilisateur avec l'ID {user_id} n'existe pas.")
            message = f"Échec : L'utilisateur avec l'ID {user_id} n'existe pas."

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur SQL lors de la suppression de l'utilisateur : {str(e)}")
        message = f"Erreur lors de la suppression de l'utilisateur : {str(e)}"

        return message
    
def delete_instrument(session, instrument_id):
    instrument = session.query(Instrument).filter_by(instrument_id=instrument_id).first()
    if not instrument:
        return "Instrument introuvable"
    
    # Ici, on pourrait ajouter une vérification : est-il lié à une partition HBM ?
    # Pour l'instant, on reste simple :
    try:
        instrument = session.query(Instrument).filter_by(instrument_id=instrument_id).first()
        if not instrument:
            return "Instrument introuvable"
        else:
            session.delete(instrument)
            message = f"Succès : Instrument '{instrument.nom}' supprimé."
    except Exception as e:
        session.rollback()
        message = f"Erreur lors de la suppression : {e}"
    return message

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
        stmt = select(Partition).options(noload('*')).where(Partition.partition_id==partition_id)
        result = session.execute(stmt)
        partition = result.first()
        session.close()
        return partition

def read_partition_by_id_complete(session, partition_id):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    stmt = select(Partition).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id).add_columns(AssAuteurPartition.role)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur).where(Partition.partition_id==partition_id).distinct()
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_composer(session, composer_id=None, name=None):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    name=f"%{name}%"
    stmt = select(Partition.partition_id, Partition.titre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id).add_columns(Auteur.prenom, Auteur.nom).where(and_(AssAuteurPartition.role=='compositeur', or_(Auteur.auteur_id==composer_id, Auteur.nom.ilike(name))))
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_arranger(session, arranger_id=None, name=None):
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
    # les champs sont retournés null
    # stmt = select(Partition).options(noload('*'))\
    #     .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
    #     .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
    #     .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
    #     .where(Partition.niveau==grade)
    
    stmt = select(Partition.partition_id, Partition.titre, Partition.sous_titre,Partition.edition, Partition.collection, \
                Partition.instrumentation, Partition.niveau, Partition.genre, \
                Partition.style, Partition.annee_sortie, Partition.ISMN, Partition.ref_editeur,\
                Partition.duree, Partition.description, Partition.url)\
        .options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, (Auteur.prenom + " " + Auteur.nom).label("auteur_nom_complet"))\
        .where(Partition.niveau==grade)
    result = session.execute(stmt)
    partition = result.all()
    session.close()
    return partition

def read_partition_by_genre(session, genre):
    # l'option noload permet de ne pas charger les relations avec les autres tables
    genre=f"%{genre}%"
    stmt = select(Partition.partition_id, Partition.titre, Partition.genre).options(noload('*'))\
        .join(AssAuteurPartition, AssAuteurPartition.partition_id==Partition.partition_id)\
        .join(Auteur, AssAuteurPartition.auteur_id==Auteur.auteur_id)\
        .add_columns(AssAuteurPartition.role, Auteur.prenom + " " + Auteur.nom)\
        .where(Partition.genre.ilike(genre))
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


# user complet pour admin
def read_user_by_id(session, user_id):
    stmt = select(User).where(User.user_id==user_id)
    result = session.execute(stmt)
    user = result.first()
    return user

def read_user_by_pseudo(session, pseudo):
    stmt = select(User.pseudo, User.fullname, User.email).where(User.pseudo==pseudo)
    result = session.execute(stmt)
    user = result.first()
    return user

# tables complètes
def read_auteur_all(session):
    return session.query(Auteur).all()

def read_partition_all(session):
    return session.query(Partition).all()

def read_partition_possessed_all(session):
    return session.query(PartitionHBM).all()

def read_event_all(session):
    return session.query(Evenement).all()

def read_asso_partition_event_all(session):
    return session.query(AssEvenementHbm).all()

def read_asso_auteur_partition_all(session):
    return session.query(AssAuteurPartition).all()

def read_instrument_all(session):
    return session.query(Instrument).all()

# ******** UPDATE / PUT ********
# A FINIR
def update_event(session, event_id, date_evenement=None, nom_evenement=None, lieu=None, type_evenement=None, affiche=None):
    try:
        existing_event = session.query(Evenement).filter_by(evenement_id = event_id).first()

        if existing_event:    
            stmt = update(Evenement).where(
                Evenement.evenement_id == event_id).values(
                    date_evenement=date_evenement,
                    nom_evenement=nom_evenement,
                    lieu=lieu,
                    type_evenement=type_evenement,
                    affiche=affiche
                )
            session.execute(stmt) 
            message = "L'événement a été mis à jour"
            session.commit()
        else:
            message = "L'événement n'existe pas"

    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        message = f"Erreur lors de la mise à jour de l'enregistrement : {e}"
    finally:
        # Fermeture de la session
        session.close()
    return message

def update_partition_hbm(session, partition_hbm_id):
    pass

def update_partition(session, partition_id):
    pass

def update_auteur(session, author_id):
    pass

def update_user_sample(session, pseudo, fullname, password, email):
    pass

def update_user_complete(session, user_id, pseudo, fullname, email, permissions):
    pass

if __name__ == "__main__":
    # from E4.harmonie.BDD.database import sql_connect
    SessionLocal = sql_connect()
    session = SessionLocal()
    create_auteur(session, nom="Zola", prenom="Emile")
    # delete_user(session,7)
    session.commit()
    session.close()
# with open("database.py") as m:
#     code = m.read()
# exec(code)
# session=SessionLocal()
# print(read_event_by_id(session, 10))
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
# create_event(session,datetime.strptime("03-10-2025", "%d-%m-%Y").date(),"semaine découverte", "auditorium CACFM", "concert","" )
# update_event(session, 32, datetime.strptime("03-10-2025", "%d-%m-%Y").date(), "modif", "ailleurs", "défilé","mon_affiche.jpg")
# session.commit()
# session.close()

# Session = sql_connect()
# session = Session()
# print(read_partition_by_creation_date(session, 2024))
# # session.commit()
# session.close()