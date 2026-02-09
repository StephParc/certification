# create_db.py
import csv
import os
from datetime import date, datetime
from pathlib import Path

from E4.harmonie.BDD.database import get_session_sql, sql_connect, get_engine
from E4.harmonie.BDD.crud import create_event, create_part, create_auteur, create_asso_auteur_partition, create_user_admin, create_instrument
from E4.harmonie.BDD.api_externe import get_api_externe
from E4.harmonie.BDD.models import Base
from E4.harmonie.BDD.config import REJET_IMPORT_PATH
from utils.logger_config import setup_logger, trace_action
from utils.utils_functions import write_rejection_log

logger_name = "E4 - Insertion BDD"
logger = setup_logger(logger_name)

# timenow = datetime.now()
# file_name = f"{str(timenow)} - rejets_import_scrapy.csv"
# REJET_IMPORT_FILE = Path(__file__).parent / file_name

# # session = get_session_sql()
# SessionLocal= sql_connect()
# session = SessionLocal()

# # Exécution du script princpal models.py      
# with open("models.py") as m:
#     code = m.read()
# exec(code)

@trace_action(logger_name)
def init_db():
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("BDD initialisée")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la BDD : {e}")

# Insertion du csv évènements dans BDD
@trace_action(logger_name)
def insert_event_to_db(file_path):
    """
    Insert events from a CSV file into the database.

    This function reads a CSV file containing event data, processes each row to extract event details,
    and inserts these details into the database using a session. Each row in the CSV file should contain
    fields for the event date, name, location, type, and poster. If an error occurs during the process,
    any changes made are rolled back to maintain database integrity.

    Args:
        file_path (str): The path to the CSV file containing event data. The CSV file should have columns
                         named 'date_event', 'nom_event', 'lieu', 'type_event', and 'affiche'.

    Side Effects:
        - Commits changes to the database if all rows are processed successfully.
        - Rolls back changes if an error occurs during processing.
        - Prints an error message if an exception is raised during the process.

    Notes:
        - The date in the CSV file should be in the format "%d-%m-%Y".
        - This function assumes the existence of a `create_event` function to handle the insertion of
          individual events into the database.
    """
    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                date_evenement = datetime.strptime(row.get('date_event'), "%d-%m-%Y").date()
                nom_evenement = row.get('nom_event')
                lieu = row.get('lieu')
                type_evenement = row.get('type_event')
                affiche = row.get('affiche')
                create_event(session, date_evenement=date_evenement, nom_evenement=nom_evenement, lieu=lieu, type_evenement=type_evenement, affiche=affiche)    
 
        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        logger.error(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

# @trace_action(logger_name)
# def log_rejection_import(row_data, error_msg):
#     file_exists = REJET_IMPORT_FILE.exists()
#     try:
#         with open(REJET_IMPORT_FILE, "a", newline='', encoding='utf-8') as f:
#             fieldnames = list(row_data.keys()) + ["erreur_import"]
#             writer = csv.DictWriter(f, fieldnames=fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             row_data["erreur_import"] = error_msg
#             writer.writerow(row_data)
#     except Exception as e:
#         logger.error(f"Impossible d'écrire dans le fichier de rejet: {e}")

@trace_action(logger_name)
def insert_scrapy_to_db(file_path):
    """
    Insert music partition data from a CSV file into the database.

    This function reads a CSV file containing music partition data, processes each row to extract
    partition details, and inserts these details into the database. It also handles associated
    authors such as composers, artists, and arrangers by querying an external API for additional
    information. Each author's details are inserted into the database and associated with the
    respective partition.

    Args:
        file_path (str): The path to the CSV file containing music partition data. The CSV file should
                         have columns named 'titre', 'sous_titre', 'edition', 'collection',
                         'instrumentation', 'niveau', 'genre', 'style', 'annee_sortie', 'ISMN',
                         'ref_editeur', 'duree', 'description', 'url', 'compositeur', 'artiste',
                         and 'arrangeur'.

    Side Effects:
        - Commits changes to the database if all rows are processed successfully.
        - Rolls back changes if an error occurs during processing.
        - Prints an error message if an exception is raised during the process.

    Notes:
        - The 'niveau' and 'annee_sortie' fields should be numeric and are converted to float and int,
          respectively.
        - The function assumes the existence of helper functions such as `create_part`,
          `create_auteur`, `get_api_externe`, and `create_asso_auteur_partition` to handle the insertion
          and association of data within the database.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_rejet_file = REJET_IMPORT_PATH.with_name(f"{timestamp}_{REJET_IMPORT_PATH.name}")

    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            count_ok = 0
            count_err = 0

            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                etape = "Initialisation"
                try:
                    etape = "Parsing des données"
                    # déclarations des variables
                    titre=row.get('titre').upper() if row.get('titre') else None
                    sous_titre=row.get('sous_titre')
                    edition=row.get('edition')
                    collection=row.get('collection')
                    instrumentation=row.get('instrumentation')
                    niveau=float(row['niveau']) if row.get('niveau') else None
                    genre=row.get('genre')
                    style=row.get('style')
                    annee_sortie=int(row['annee_sortie']) if row.get('annee_sortie') else None
                    ISMN=row.get('ISMN')
                    ref_editeur=row.get('ref_editeur')
                    duree=row.get('duree')
                    description=row.get('description')
                    url=row.get('url')

                    etape = "Création partition"
                    part = create_part(session, titre=titre,sous_titre=sous_titre, edition=edition,
                                       collection=collection,instrumentation=instrumentation, niveau=niveau,
                                       genre=genre, style=style, annee_sortie=annee_sortie, ISMN=ISMN,
                                       ref_editeur=ref_editeur, duree=duree, description=description, url=url)
                    part_id = part.partition_id

                    mapping_auteurs = {
                        'compositeur': row.get('compositeur', '').split(","),
                        'artiste': row.get('artiste', '').split(","),
                        'arrangeur': row.get('arrangeur', '').split(",")
                    }

                    for role, noms in mapping_auteurs.items():
                        etape = f"Traitement {role}"
                        for nom_brut in noms:
                            nom_brut = nom_brut.strip()
                            if not nom_brut:
                                continue
                            
                            etape = f"Traitement {role}: {nom_brut}"
                            auteur = create_auteur(session, nom=nom_brut)
                            
                            # Association
                            etape = f"Association {role}: {nom_brut}"
                            create_asso_auteur_partition(session, part_id, auteur.auteur_id, role)
                    
                    session.commit()
                    count_ok += 1

                except Exception as e:
                    # En cas d'erreur, annuler les changements
                    session.rollback()
                    count_err += 1
                    error_detail = f"[{etape}] - {str(e)}"
                    # log_rejection_import(row, error_detail)
                    headers = list(row.keys()) + ["erreur_import"]
                    row_data = list(row.values()) + [error_detail]
                    write_rejection_log(str(current_rejet_file), headers, row_data)
                    logger.warning(f"Ligne rejetée vers {current_rejet_file.name}")

                    # logger.warning(f"Ligne rejetée : {titre} | Raison: {error_detail}")

            logger.info(f"Importation terminée. Succès: {count_ok}, Echecs: {count_err}")
    
    except Exception as e:
        logger.error(f"Erreur à l'ouverture du fichier: {e}")
    finally:
        # Fermeture de la session
        session.close()  
    
# Insertion du csv users dans BDD, uniquement à des fins de démonstration
@trace_action(logger_name)
def insert_users_to_db(file_path):
    """
    Insert user data from a CSV file into the database.

    This function reads a CSV file containing user data, processes each row to extract user details,
    and inserts these details into the database using a session. Each row in the CSV file should contain
    fields for the username, full name, hashed password, email, and permissions. If an error occurs during
    the process, any changes made are rolled back to maintain database integrity.

    Args:
        file_path (str): The path to the CSV file containing user data. The CSV file should have columns
                         named 'username', 'fullname', 'hashed_password', 'email', and 'permissions'.

    Side Effects:
        - Commits changes to the database if all rows are processed successfully.
        - Rolls back changes if an error occurs during processing.
        - Prints an error message if an exception is raised during the process.

    Notes:
        - This function assumes the existence of a `create_user_admin` function to handle the insertion of
          individual user records into the database.
        - The function uses a session to interact with the database, which is closed after the operation
          completes, regardless of success or failure.
    """
    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                pseudo = row.get('pseudo')
                fullname = row.get('fullname')
                hashed_password = row.get('hashed_password')
                email = row.get('email')
                permissions = row.get('permissions')
                create_user_admin(session, pseudo=pseudo, fullname=fullname, hashed_password=hashed_password, email=email, permissions=permissions)    
 
        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        logger.error(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

# Insertion du csv instruments dans BDD, uniquement à des fins de démonstration
@trace_action(logger_name)
def insert_instruments_to_db(file_path):
    SessionLocal = sql_connect()
    session = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                nom = row.get('nom').strip()
                famille = row.get('famille').strip()
                sous_famille = row.get('sous_famille').strip() # Récupération
                create_instrument(session, nom=nom,famille=famille,sous_famille=sous_famille)
                    
        session.commit()
        logger.info(f"Import des instruments réussi (nom/famille/sous_famille)")
    except Exception as e:
        session.rollback()
        logger.error(f"Erreur lors de l'importation des instruments : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    user_file = Path("E4/harmonie/sources/users.csv")
    insert_users_to_db(user_file)
    # scrapy_file = Path("E4/harmonie/harmonie/musicshop_last.csv")
    # insert_scrapy_to_db(scrapy_file)
    scrapy_file = Path("E4/harmonie/harmonie/fichier_base_test.csv")
    insert_scrapy_to_db(scrapy_file)
    event_file = Path("E4/harmonie/sources/events.csv")
    insert_event_to_db(event_file)
    instru_file = Path("E4/harmonie/sources/instruments.csv")
    insert_instruments_to_db(instru_file)

# Chemins vers les fichiers CSV
# promt au niveau de BDD/
# event_path = "../sources/events.csv"
# scrapy_path = "../harmonie/musicshop_new.csv"
# user_path = "../sources/users.csv"

# Importation des données CSV dans la base de données
# insert_event_to_db(event_path)
# insert_scrapy_to_db(scrapy_path)
# insert_users_to_db(user_path)