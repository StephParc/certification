# Paramétrages que j'ai appliqués

## WinSCP

Lancer WinSCP.  
Ouvrir un nouvel onglet pour créer une connexion (nom personnalisable).  
Choisir le protocole: Amazone S3  
pas de chiffrement  
nom d'hôte: localhost  
port: 3900  
ID de la clé d'accès: KEY_ID_DL_RW (automatiquement complétée dans le .env)  
Clé d'accès secrète: SECRET_KEY_DL_RW (automatiquement complétée dans le .env)  
Dans les paramètres avancés:  
style URL: chemin  
région (optionnel): garage  
Au moment de sauver, vous pouvez choisir de créer un raccourci bureau et également de sauvegarder les identifiants.  


## DBeaver

host: localhost  
port: 5433 (identique au docker-compose.yml service postgres)  
nom d'utilisateur: DBUSER_RW (choisi dans .env)
mot de passe:  PASSWORD_RW (choisi dans .env)  

## MongoDB Compass

MONGO_USER et MONGO_PASSWORD chosis dans le .env
URI: mongodb://${MONGO_USER}:${MONGO_PASSWORD}@dlocalhost:27018/?authSource=admin"


## Docker Desktop