# sync_sql_mongo.py
import os
import sys
import argparse
import csv
import secrets
import string
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Union

from E4.harmonie.BDD.database import get_mongo_db, sql_connect
from E4.harmonie.BDD.models import User, Instrument, PartitionHBM, Partition
from E4.harmonie.BDD.auth import get_password_hash
from E4.harmonie.BDD.config import REJET_INSTRUMENTS_PATH, USER_LOG_PATH, RECONCILIATION_PARTITIONS_PATH
from utils.logger_config import setup_logger, trace_action
from utils.utils_functions import write_rejection_log

logger_name = "Synchronisation hbm mongoHbm"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def main():
    parser = argparse.ArgumentParser(description="Synchronisation uuid")
    # Premier argument : l'action à réaliser
    parser.add_argument(
        "action", 
        choices=["sync_instruments", "sync_musiciens", "sync_partitions"],
        help="Collection à sychroniser"
    )
    
    # Second argument optionnel : le chemin du fichier (requis pour les imports)
    parser.add_argument(
        "--file", 
        type=str,
        help="Chemin relatif du fichier de rejets"
    )

    args = parser.parse_args()

    # Logique de routage des commandes
    try:
        if args.action == "sync_instruments":
            logger.info("--- Synchronisation des instruments ---")
            sync_instruments_with_creation(REJET_INSTRUMENTS_PATH)
            
        elif args.action == "sync_musiciens":
            logger.info("--- Synchronisation des musiciens ---")
            if not args.file: raise ValueError("Le flag --file est requis pour cet import.")
            sync_musicians_with_creation(USER_LOG_PATH)
            
        elif args.action == "sync_partitions":
            logger.info("--- Synchronisation des partitions ---")
            if not args.file: raise ValueError("Le flag --file est requis pour cet import.")
            sync_partitions_hbm_uuids(RECONCILIATION_PARTITIONS_PATH)

        logger.info(f"Succès : Action '{args.action}' terminée.")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de '{args.action}': {e}", file=sys.stderr)
        sys.exit(1)

@trace_action(logger_name)
def sync_instruments_with_creation(rejet_path: Union[str, Path]):
    """
    Synchronise les UUIDs entre COL_instruments et TB_instrument.
    Si l'instrument n'existe pas en SQL, il est créé (champs famille/sous_famille à None).
    """
    rejet_path = str(rejet_path)

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()
    
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
            write_rejection_log(rejet_path, headers, row)

            logger.warning(f"Instrument créé et ajouté au rejet : {nom_sql}")

        # Mise à jour de COL_instruments avec l'UUID de TB_instrument
        db_mongo["COL_instruments"].update_one(
            {"_id": inst_doc["_id"]},
            {"$set": {"instrument_uuid": str(inst_sql.instrument_uuid)}}
        )
    
    session.commit()
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
def sync_musicians_with_creation(log_path: Union[str, Path]):
    """
    Synchronise COL_musiciens et TB_utilisateur. 
    Crée l'utilisateur SQL s'il manque et logue les credentials.
    """
    log_path =str(log_path)

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()
      
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
            write_rejection_log(log_path, headers, row)

        # Mise à jour MongoDB avec l'UUID de SQL 
        db_mongo["COL_musiciens"].update_one(
            {"_id": m_doc["_id"]},
            {"$set": {"user_uuid": str(user_sql.user_uuid)}}
        )
        
    session.commit()
    session.close()

@trace_action(logger_name)
def sync_partitions_hbm_uuids(rejet_path: Union[str, Path]):
    """
    Tente de lier COL_partitions à TB_partition_hbm par le titre. [cite: 11, 14]
    Si le titre est ambigu ou absent de SQL, l'ajoute au fichier de réconciliation.
    """
    rejet_path = str(rejet_path)

    db_mongo = get_mongo_db()
    SessionLocal = sql_connect()
    session = SessionLocal()
    
    partitions_mongo = db_mongo["COL_partitions"].find({"hbm_uuid": {"$exists": False}})

    for p_doc in partitions_mongo:
        titre_mongo = p_doc.get("titre").upper()
        
        # On cherche d'abord si le titre existe dans le catalogue (TB_partition)
        partitions_sql = session.query(Partition).filter(func.upper(Partition.titre)==titre_mongo).all()

        if len(partitions_sql) > 1:
            # CAS AMBIGU : Plusieurs partitions portent ce nom
            headers = ["mongo_id", "titre", "motif", "date_rejet"]
            row = [str(p_doc["_id"]), titre_mongo, "Ambiguïté Catalogue", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            write_rejection_log(rejet_path, headers, row)
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
    session.close()

if __name__ == "__main__":
    main()