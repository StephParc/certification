# init_mongo.py
"""
NoSQL Environment Setup and Data Seed Service.

This module initializes the MongoDB environment for the Harmonie platform. 
It provides idempotent setup routines to ensure the document database 
is correctly structured and populated before the application starts.

Key Features:
1. Environment Reset: Ability to purge the existing database for 
   clean development iterations.
2. Automated Seeding: Imports core collections (Musicians, Instruments, 
   Partitions) from a centralized JSON source.
3. Cross-Module Integration: Utilizes the shared MongoDB client 
   configuration from the database layer.
"""
import json
import os
from pymongo import MongoClient

from config.config import MONGO_DATABASE_URL, MONGO_DBNAME
from E4.harmonie.BDD.database import get_mongo_client, get_mongo_db
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - MongoDB"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def reset_database():
    """
    Purges the target MongoDB database.
    Drops the entire database defined in the configuration to allow 
    a fresh start during deployment or testing.
    """
    client = get_mongo_client()
    client.drop_database(MONGO_DBNAME)
    logger.info(f"Base de données '{MONGO_DBNAME}' supprimée avec succès.")

@trace_action(logger_name)
def import_from_json(file_path):
    """
    Seeds MongoDB collections from a JSON file.

    Parses the input file where keys represent collection names and 
    values represent lists of documents. Uses 'insert_many' for 
    efficient bulk loading.

    Args:
        file_path (str): Path to the JSON source file containing 
                         the collection definitions.
    """
    db = get_mongo_db()
    
    if not os.path.exists(file_path):
        logger.error(f"Erreur : Le fichier {file_path} est introuvable.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Iterates through JSON keys to map documents to MongoDB collections
    for collection_name, documents in data.items():
        if documents:
            result = db[collection_name].insert_many(documents)
            logger.info(f"{len(result.inserted_ids)} documents importés dans '{collection_name}'.")

if __name__ == "__main__":
    SOURCE_FILE = "E4/harmonie/sources/collections.json"
    
    # Execution sequence: Reset followed by Import
    reset_database()
    import_from_json(SOURCE_FILE)