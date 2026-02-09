# crud_mongo.py
from bson import ObjectId
from E4.harmonie.BDD.database import get_mongo_db
from E4.harmonie.BDD.crud import create_user_admin
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - Manipulation collections mongoHbm"
logger = setup_logger(logger_name)

# ******** CREATE / POST ********
@trace_action(logger_name)
def create_one_document(collection_name: str, data: dict):
    """
    Fonction générique pour insérer n'importe quel document 
    dans une collection.
    """
    db = get_mongo_db()
    collection = db[collection_name]
    
    result = collection.insert_one(data)
    logger.info(f"Document ajouté à la collection {collection_name}")
    
    # On retourne l'ID pour confirmer que ça a marché
    return str(result.inserted_id)

# ******** READ / GET ********
def get_one_document(collection_name: str, query: dict):
    """
    Récupère un seul document correspondant au filtre 'query'.
    Exemple query: {"email": "test@test.com"} ou {"_id": ObjectId(id_str)}
    """
    db = get_mongo_db()
    return db[collection_name].find_one(query)

def get_many_documents(collection_name: str, query: dict = None, limit: int = 0):
    """
    Récupère plusieurs documents. Si query est None, récupère tout.
    """
    db = get_mongo_db()
    query = query or {}
    # .find() retourne un curseur, on le transforme en liste
    return list(db[collection_name].find(query).limit(limit))

def get_visible_musicians(requester_uuid: str, is_admin: bool):
    """
    Logique de filtrage :
    - Admin : voit tout le monde.
    - Musicien : voit les profils avec 'accord_donnees_perso': True + son propre profil.
    """
    db = get_mongo_db()
    
    if is_admin:
        # L'admin voit tout
        query = {}
    else:
        # Le musicien voit ceux qui ont accepté OU lui-même
        query = {
            "$or": [
                {"accord_donnees_perso": True},
                {"user_uuid": requester_uuid}
            ]
        }
    
    cursor = db["COL_musiciens"].find(query)
    return list(cursor)

def get_partition_by_uuid(hbm_uuid: str):
    """Récupère la nomenclature Mongo via l'identifiant SQL."""
    db = get_mongo_db() #
    # On cherche le document lié
    return db["COL_partitions"].find_one({"hbm_uuid": hbm_uuid})

# ******** UPDATE / PUT ********
@trace_action(logger_name)
def update_one_document(collection_name: str, filter_query: dict, update_data: dict):
    """
    Met à jour un document. 
    Note : On utilise l'opérateur "$set" pour ne modifier que les champs envoyés.
    """
    db = get_mongo_db()
    result = db[collection_name].update_one(
        filter_query, 
        {"$set": update_data}
    )
    logger.info(f"{collection_name} mis à jour pour {filter_query}")
    return result.modified_count > 0

def link_partition_hbm_to_mongo(mongo_id: str, hbm_uuid: str):
    """
    Réalise le 'mariage' manuel entre un document Mongo et une ligne SQL.
    C'est un simple update du champ hbm_uuid dans COL_partitions.
    """
    db_mongo = get_mongo_db()
    
    try:
        # On utilise update_one avec l'opérateur $set pour ne pas écraser le reste du doc
        # On convertit le mongo_id (string) en ObjectId pour MongoDB
        result = db_mongo["COL_partitions"].update_one(
            {"_id": ObjectId(mongo_id)},
            {"$set": {"hbm_uuid": hbm_uuid}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Liaison manuelle réussie : Mongo[{mongo_id}] <-> SQL[{hbm_uuid}]")
            return True
        else:
            logger.warning(f"Aucune modification : le document {mongo_id} n'existe pas ou a déjà cet UUID.")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la liaison manuelle : {e}")
        return False

# ******** DELETE / DELETE ********
@trace_action(logger_name)
def delete_one_document(collection_name: str, filter_query: dict):
    """
    Supprime un document correspondant au filtre.
    """
    db = get_mongo_db()
    result = db[collection_name].delete_one(filter_query)
    logger.info(f"Document {collection_name} supprimé pour {filter_query}")
    return result.deleted_count > 0

if __name__ == "__main__":
    doc = create_one_document("COL_instruments", {"nom_sql": "Célestat"})
