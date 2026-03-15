# crud_mongo.py
"""
NoSQL Data Access Object (DAO) for MongoDB.

This module provides a generic and specialized interface for interacting 
with the MongoDB database. It handles standard CRUD operations and 
implements specific business logic for:
1. Privacy-aware musician profile filtering (GDPR compliance).
2. Hybrid data linking between SQL UUIDs and NoSQL ObjectIds.
3. Automated action tracing and logging for all write operations.
"""
from bson import ObjectId
from E4.harmonie.BDD.database import get_mongo_db
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - Manipulation collections mongoHbm"
logger = setup_logger(logger_name)

# ******** CREATE / POST ********
@trace_action(logger_name)
def create_one_document(collection_name: str, data: dict):
    """
    Generic function to insert a document into a specific collection.

    Args:
        collection_name (str): Name of the target MongoDB collection.
        data (dict): Dictionary representing the document to insert.

    Returns:
        str: The string representation of the inserted document's ObjectId.
    """
    db = get_mongo_db()
    collection = db[collection_name]
    
    result = collection.insert_one(data)
    logger.info(f"Document added to collection {collection_name}")
    
    return str(result.inserted_id)

# ******** READ / GET ********
def get_one_document(collection_name: str, query: dict):
    """
    Retrieves a single document matching the provided query filter.

    Args:
        collection_name (str): Name of the collection to search in.
        query (dict): MongoDB query filter (e.g., {"user_uuid": "..."}).

    Returns:
        dict: The retrieved document or None if no match is found.
    """
    db = get_mongo_db()
    return db[collection_name].find_one(query)

def get_many_documents(collection_name: str, query: dict = None, limit: int = 0):
    """
    Retrieves multiple documents from a collection.

    Args:
        collection_name (str): Name of the collection.
        query (dict, optional): Filter criteria. Defaults to None (returns all).
        limit (int, optional): Maximum number of documents to return.

    Returns:
        list: A list of documents matching the criteria.
    """
    db = get_mongo_db()
    query = query or {}
    # .find() retourne un curseur, on le transforme en liste
    return list(db[collection_name].find(query).limit(limit))

def get_visible_musicians(requester_uuid: str, is_admin: bool):
    """
    Implements GDPR-compliant filtering logic for musician profiles.

    Visibility rules:
    - Admins: Can view all musician profiles in the collection.
    - Musicians: Can only view profiles where 'accord_donnees_perso' is True, 
      plus their own profile regardless of consent status.

    Args:
        requester_uuid (str): The UUID of the user making the request.
        is_admin (bool): True if the requester has administrative privileges.

    Returns:
        list: Filtered list of visible musician documents.
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
    """
    Retrieves technical partition nomenclature using the SQL-linked UUID.

    Args:
        hbm_uuid (str): The unique identifier used to link SQL and NoSQL records.

    Returns:
        dict: The MongoDB document containing technical partition details.
    """
    db = get_mongo_db()
    return db["COL_partitions"].find_one({"hbm_uuid": hbm_uuid})

# ******** UPDATE / PUT ********
@trace_action(logger_name)
def update_one_document(collection_name: str, filter_query: dict, update_data: dict):
    """
    Updates a specific document using the '$set' operator for partial updates.

    Args:
        collection_name (str): Collection name.
        filter_query (dict): Criteria to identify the document to update.
        update_data (dict): Key-value pairs to update.

    Returns:
        bool: True if at least one document was modified, False otherwise.
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
    Performs the manual linkage ('marriage') between a NoSQL document and a SQL record.

    Updates the 'hbm_uuid' field in the 'COL_partitions' document to establish 
    the relationship used in hybrid API views.

    Args:
        mongo_id (str): The MongoDB ObjectId (as a string).
        hbm_uuid (str): The SQL-generated UUID to link.

    Returns:
        bool: True if the linkage was successful.
    """
    db_mongo = get_mongo_db()
    
    try:
        # On convertit le mongo_id (string) en ObjectId pour MongoDB
        result = db_mongo["COL_partitions"].update_one(
            {"_id": ObjectId(mongo_id)},
            {"$set": {"hbm_uuid": hbm_uuid}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Manual link success: Mongo[{mongo_id}] <-> SQL[{hbm_uuid}]")
            return True
        else:
            logger.warning(f"No modification: document {mongo_id} not found or already linked.")
            return False
            
    except Exception as e:
        logger.error(f"Error during manual linkage: {e}")
        return False

# ******** DELETE / DELETE ********
@trace_action(logger_name)
def delete_one_document(collection_name: str, filter_query: dict):
    """
    Removes a single document from a collection based on a filter.

    Args:
        collection_name (str): Collection name.
        filter_query (dict): Criteria to identify the document to delete.

    Returns:
        bool: True if a document was deleted, False otherwise.
    """
    db = get_mongo_db()
    result = db[collection_name].delete_one(filter_query)
    logger.info(f"Document {collection_name} deleted for {filter_query}")
    return result.deleted_count > 0

