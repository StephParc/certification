# init_mongo.py
import json
import os
from pymongo import MongoClient

from E4.harmonie.BDD.config import MONGO_DATABASE_URL, MONGO_DBNAME
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - MongoDB"
logger = setup_logger(logger_name)

def get_mongo_client():
    """Crée et retourne le client MongoDB."""
    return MongoClient(MONGO_DATABASE_URL)

@trace_action(logger_name)
def reset_database():
    """Supprime la base de données pour repartir de zéro."""
    client = get_mongo_client()
    client.drop_database(MONGO_DBNAME)
    logger.info(f"Base de données '{MONGO_DBNAME}' supprimée avec succès.")

@trace_action(logger_name)
def import_from_json(file_path):
    """Importe les données d'un fichier JSON dans les collections correspondantes."""
    client = get_mongo_client()
    db = client[MONGO_DBNAME]
    
    if not os.path.exists(file_path):
        logger.error(f"Erreur : Le fichier {file_path} est introuvable.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # On boucle sur les clés du JSON (musiciens, instruments, partitions)
    for collection_name, documents in data.items():
        if documents:
            # On insère les documents dans la collection du même nom
            result = db[collection_name].insert_many(documents)
            logger.info(f"{len(result.inserted_ids)} documents importés dans '{collection_name}'.")

if __name__ == "__main__":
    SOURCE_FILE = "E4/harmonie/sources/collections.json"
    
    # Exécution en deux étapes distinctes
    reset_database()
    import_from_json(SOURCE_FILE)