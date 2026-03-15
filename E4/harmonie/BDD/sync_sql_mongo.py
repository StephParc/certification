# sync_sql_mongo.py
"""
Database Synchronization & UUID Reconciliation Service.

This CLI utility ensures referential integrity across the hybrid 
PostgreSQL/MongoDB architecture. It performs three critical tasks:
1. Instrument Alignment: Bridges relational and document-based instrument data.
2. User Provisioning: Automatically creates SQL user accounts for musicians 
   discovered in the NoSQL database.
3. Partition Linking: Establishes the HBM_UUID link for the music catalog.
"""
import sys
import argparse
import secrets
import string
from datetime import datetime
from sqlalchemy import func

from E4.harmonie.BDD.database import get_mongo_db, sql_connect
from E4.harmonie.BDD.models import User, Instrument, PartitionHBM, Partition
from E4.harmonie.BDD.auth import get_password_hash
from config.config import REJET_INSTRUMENTS_PATH, USER_LOG_PATH, RECONCILIATION_PARTITIONS_PATH
from utils.logger_config import setup_logger, trace_action
from utils.utils_functions import write_rejection_log
from utils.S3_utils import upload_file

logger_name = "Synchronisation hbm mongoHbm"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def main():
    parser = argparse.ArgumentParser(description="Synchronisation uuid")
    # L'action à réaliser
    parser.add_argument(
        "action", 
        choices=["sync_instruments", "sync_musiciens", "sync_partitions"],
        help="Collection à sychroniser"
    )
    
    args = parser.parse_args()

    # Logique de routage des commandes
    try:
        if args.action == "sync_instruments":
            logger.info("--- Synchronisation des instruments ---")
            sync_instruments_with_creation()
            
        elif args.action == "sync_musiciens":
            logger.info("--- Synchronisation des musiciens ---")
            sync_musicians_with_creation()
            
        elif args.action == "sync_partitions":
            logger.info("--- Synchronisation des partitions ---")
            sync_partitions_hbm_uuids()

        logger.info(f"Succès : Action '{args.action}' terminée.")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de '{args.action}': {e}", file=sys.stderr)
        sys.exit(1)

@trace_action(logger_name)
def sync_instruments_with_creation():
    """
    Synchronise les UUIDs entre COL_instruments et TB_instrument.
    Si l'instrument n'existe pas en SQL, il est créé (champs famille/sous_famille à None).
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_rejet_file = REJET_INSTRUMENTS_PATH.with_name(f"{timestamp}_{REJET_INSTRUMENTS_PATH.name}")

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()
    
    try:
        instruments_mongo = db_mongo["COL_instruments"].find({"instrument_uuid": {"$exists": False}})
        
        for inst_doc in instruments_mongo:
            nom_sql = inst_doc.get("nom_sql") #
            
            # Recherche dans TB_instrument
            inst_sql = session.query(Instrument).filter_by(nom=nom_sql).first() 
            
            if not inst_sql:
                # Création SQL
                inst_sql = Instrument(nom=nom_sql, famille=None, sous_famille=None)
                session.add(inst_sql)
                session.flush()
                
                headers = ["nom_sql", "uuid", "time_rejet"]
                row = [nom_sql, str(inst_sql.instrument_uuid), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                write_rejection_log(current_rejet_file, headers, row)

                logger.warning(f"Instrument créé et ajouté au rejet : {nom_sql}")

            # Mise à jour de COL_instruments avec l'UUID de TB_instrument
            db_mongo["COL_instruments"].update_one(
                {"_id": inst_doc["_id"]},
                {"$set": {"instrument_uuid": str(inst_sql.instrument_uuid)}}
            )
        session.commit()
        if current_rejet_file.exists():
            s3_rejet_path = f"rejets/E4/sync/{current_rejet_file.name}"
            upload_file(str(current_rejet_file), "zone-maintenance", s3_rejet_path)
            logger.info(f"Fichier de rejet disponible sur S3: zone-maintenance/{s3_rejet_path}")

    except Exception as e:
        session.rollback()
        logger.error(f"Erreur synchro: {e}")
        raise
    finally:
        session.close()

def generate_unique_pseudo(session, prenom, nom):
    # Nettoyage de base : minuscule et remplacement des espaces par des underscores
    base_pseudo = f"{prenom.lower()}_{nom.lower()}".replace(" ", "_")
    pseudo = base_pseudo
    counter = 1
    
    # Vérification d'unicité dans TB_utilisateur 
    while session.query(User).filter_by(pseudo=pseudo).first():
        pseudo = f"{base_pseudo}_{counter}"
        counter += 1
    return pseudo

@trace_action(logger_name)
def sync_musicians_with_creation():
    """
    Synchronise COL_musiciens et TB_utilisateur. 
    Crée l'utilisateur SQL s'il manque et logue les credentials.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_rejet_file = USER_LOG_PATH.with_name(f"{timestamp}_{USER_LOG_PATH.name}")

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()

    try:  
        # Récupération des musiciens sans UUID 
        musiciens_mongo = db_mongo["COL_musiciens"].find({"user_uuid": {"$exists": False}})
        
        for m_doc in musiciens_mongo:
            email = m_doc.get("email") # 
            user_sql = session.query(User).filter_by(email=email).first() # 
            
            if not user_sql:
                # Génération des credentials par défaut
                # Mot de passe aléatoire (12 caractères)
                alphabet = string.ascii_letters + string.digits
                raw_password = ''.join(secrets.choice(alphabet) for _ in range(12))
                
                # Pseudo par défaut 
                new_pseudo = generate_unique_pseudo(session, m_doc.get('prenom'), m_doc.get('nom'))
                
                # Création SQL 
                user_sql = User(
                    pseudo=new_pseudo,
                    fullname=f"{m_doc.get('prenom')} {m_doc.get('nom')}", 
                    email=email,
                    hashed_password=get_password_hash(raw_password),
                    permissions="read_only"
                )
                session.add(user_sql)
                session.flush() 
            
                headers = ["email", "pseudo", "temp_password", "user_uuid", "date_creation"]
                row = [email, new_pseudo, raw_password, str(user_sql.user_uuid), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                write_rejection_log(current_rejet_file, headers, row)

            # Mise à jour MongoDB avec l'UUID de SQL 
            db_mongo["COL_musiciens"].update_one(
                {"_id": m_doc["_id"]},
                {"$set": {"user_uuid": str(user_sql.user_uuid)}}
            )
            
        session.commit()
        if current_rejet_file.exists():
            s3_rejet_path = f"rejets/E4/sync/{current_rejet_file.name}"
            upload_file(str(current_rejet_file), "zone-maintenance", s3_rejet_path)
            logger.info(f"Fichier de rejet disponible sur S3: zone-maintenance/{s3_rejet_path}")

    except Exception as e:
        session.rollback()
        logger.error(f"Erreur synchro: {e}")
        raise
    finally:
        session.close()

@trace_action(logger_name)
def sync_partitions_hbm_uuids():
    """
    Tente de lier COL_partitions à TB_partition_hbm par le titre. [cite: 11, 14]
    Si le titre est ambigu ou absent de SQL, l'ajoute au fichier de réconciliation.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_rejet_file = RECONCILIATION_PARTITIONS_PATH.with_name(f"{timestamp}_{RECONCILIATION_PARTITIONS_PATH.name}")

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()
    
    try: 
        partitions_mongo = db_mongo["COL_partitions"].find({"hbm_uuid": {"$exists": False}})

        for p_doc in partitions_mongo:
            titre_mongo = p_doc.get("titre").upper()
            
            # On cherche d'abord si le titre existe dans le catalogue (TB_partition)
            partitions_sql = session.query(Partition).filter(func.upper(Partition.titre)==titre_mongo).all()

            if len(partitions_sql) > 1:
                # CAS AMBIGU : Plusieurs partitions portent ce nom
                headers = ["mongo_id", "titre", "motif", "date_rejet"]
                row = [str(p_doc["_id"]), titre_mongo, "Ambiguïté Catalogue", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                write_rejection_log(str(current_rejet_file), headers, row)
                continue

            if len(partitions_sql) == 0:
                # CAS VIDE : Création dans le catalogue TB_partition 
                new_part = Partition(titre=titre_mongo, description="Créé via synchro Mongo")
                session.add(new_part)
                session.flush()
                part_sql = new_part
                logger.info(f"Créé dans TB_partition : {titre_mongo}")
            else:
                part_sql = partitions_sql[0]

            # On cherche ou on crée l'entrée dans l'inventaire (TB_partition_hbm)
            hbm_sql = session.query(PartitionHBM).filter_by(partition_id=part_sql.partition_id).first() 

            if not hbm_sql:
                hbm_sql = PartitionHBM(partition_id=part_sql.partition_id, concert=True)
                session.add(hbm_sql)
                session.flush()
                logger.info(f"Créé dans TB_partition_hbm pour : {titre_mongo}")

            # On synchronise l'hbm_uuid vers Mongo 
            db_mongo["COL_partitions"].update_one(
                {"_id": p_doc["_id"]},
                {"$set": {"hbm_uuid": str(hbm_sql.hbm_uuid)}}
            )
        session.commit()
        if current_rejet_file.exists():
            s3_rejet_path = f"rejets/E4/sync/{current_rejet_file.name}"
            upload_file(str(current_rejet_file), "zone-maintenance", s3_rejet_path)
            logger.info(f"Fichier de rejet disponible sur S3: zone-maintenance/{s3_rejet_path}")

    except Exception as e:
        session.rollback()
        logger.error(f"Erreur synchro: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()