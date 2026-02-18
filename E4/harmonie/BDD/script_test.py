from pymongo import MongoClient
from config.config import MONGO_DATABASE_URL, MONGO_DBNAME, REJET_INSTRUMENTS_PATH, USER_LOG_PATH, RECONCILIATION_PARTITIONS_PATH
from E4.harmonie.BDD.sync_sql_mongo import sync_instruments_with_creation, sync_musicians_with_creation, sync_partitions_hbm_uuids

# # 1. Connexion
# client = MongoClient(MONGO_DATABASE_URL)
# db = client[MONGO_DBNAME]
# collection = db["musiciens"]

# # 2. Préparation du document (un simple dictionnaire Python)
# nouveau_musicien = {
#     "nom": "Testeur",
#     "prenom": "Jean",
#     "email": "jean.test@example.com",
#     "competences": [
#         {"instrument": "Triangle", "niveau": "Expert"}
#     ],
#     "divers": "On peut ajouter n'importe quel champ sans prévenir !"
# }

# # 3. Insertion
# # insert_one() renvoie un objet qui contient l'ID unique généré par Mongo
# resultat = collection.insert_one(nouveau_musicien)

# print(f"Document inséré avec l'ID : {resultat.inserted_id}")


if __name__ == "__main__":
    sync_instruments_with_creation(REJET_INSTRUMENTS_PATH)
    sync_musicians_with_creation(USER_LOG_PATH)
    sync_partitions_hbm_uuids(RECONCILIATION_PARTITIONS_PATH)