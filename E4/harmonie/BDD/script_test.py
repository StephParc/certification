from pymongo import MongoClient
from E4.harmonie.BDD.config import MONGO_DATABASE_URL, MONGO_DBNAME

# 1. Connexion
client = MongoClient(MONGO_DATABASE_URL)
db = client[MONGO_DBNAME]
collection = db["musiciens"]

# 2. Préparation du document (un simple dictionnaire Python)
nouveau_musicien = {
    "nom": "Testeur",
    "prenom": "Jean",
    "email": "jean.test@example.com",
    "competences": [
        {"instrument": "Triangle", "niveau": "Expert"}
    ],
    "divers": "On peut ajouter n'importe quel champ sans prévenir !"
}

# 3. Insertion
# insert_one() renvoie un objet qui contient l'ID unique généré par Mongo
resultat = collection.insert_one(nouveau_musicien)

print(f"Document inséré avec l'ID : {resultat.inserted_id}")