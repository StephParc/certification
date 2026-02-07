# crud_mongo.py
from bson import ObjectId
from E4.harmonie.BDD.database import get_mongo_db
from E4.harmonie.BDD.crud import create_user_admin # Ton CRUD SQL existant

# ******** CREATE / POST ********
def create_one_document(collection_name: str, data: dict):
    """
    Fonction générique pour insérer n'importe quel document 
    dans une collection.
    """
    db = get_mongo_db()
    collection = db[collection_name]
    
    result = collection.insert_one(data)
    
    # On retourne l'ID pour confirmer que ça a marché
    return str(result.inserted_id)

def create_musician_hybrid(sql_session, musician_data: dict, hashed_password: str):
    """
    Crée un utilisateur dans SQL, récupère l'UUID, 
    puis crée/met à jour le document dans MongoDB.
    """
    db_mongo = get_mongo_db()

    # 1. Préparation des infos pour SQL
    pseudo = f"{musician_data['prenom'][0].lower()}_{musician_data['nom'].lower()}"
    fullname = f"{musician_data['prenom']} {musician_data['nom']}"
    
    # 2. Création SQL (Source de vérité pour l'identité)
    new_user_sql = create_user_admin(
        sql_session,
        pseudo=pseudo,
        fullname=fullname,
        email=musician_data['email'],
        hashed_password=hashed_password,
        permissions="read_only"
    )
    sql_session.commit() # On valide pour fixer l'UUID
    
    # 3. On lie Mongo à SQL via l'UUID
    musician_data["user_uuid"] = str(new_user_sql.user_uuid)
    musician_data["pseudo"] = pseudo
    
    # 4. Insertion dans Mongo
    # On utilise update_one avec upsert=True pour éviter les doublons
    db_mongo.musiciens.update_one(
        {"email": musician_data["email"]},
        {"$set": musician_data},
        upsert=True
    )
    
    return new_user_sql

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

# ******** UPDATE / PUT ********
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
    return result.modified_count > 0

# ******** DELETE / DELETE ********
def delete_one_document(collection_name: str, filter_query: dict):
    """
    Supprime un document correspondant au filtre.
    """
    db = get_mongo_db()
    result = db[collection_name].delete_one(filter_query)
    return result.deleted_count > 0

if __name__ == "__main__":
    id_mongo = "6985b9cb02a7b640cecd94ca" 
    doc = get_one_document("musiciens", {"_id": ObjectId(id_mongo)})
    print(doc["nom"])