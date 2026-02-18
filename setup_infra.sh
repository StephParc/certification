#!/bin/bash

set -a; source .env; set +a

echo "--- Préparation des dossiers ---"
mkdir -p ./dags ./logs ./plugins
# On s'assure que tout appartient à l'utilisateur actuel (1000)
sudo chown -R $(id -u):$(id -g) ./dags ./logs ./plugins

# Optionnel si poetry est installé, sinon commenter
echo "-Préparation de l'environnement ---"
if command -v poetry &> /dev/null; then
    echo "Exportation des dépendances Poetry..."
    poetry export -f requirements.txt --output requirements-app.txt --without-hashes --with app
    poetry export -f requirements.txt --output requirements-airflow.txt --without-hashes --without app
fi
# fin du bloc optionnel

echo "Nettoyage des anciens conteneurs..."
docker compose down -v

echo "Construction des images"
docker compose build --pull

# Démarrage des bases de données UNIQUEMENT
echo "Démarrage des bases de données..."
docker compose up -d db_postgres db_mongo

# Attente et création du schéma
echo "Vérification de la base de données..."
until docker exec postgres_db pg_isready > /dev/null 2>&1; do
    echo "Attente de Postgres..."
    sleep 2
done

echo "Création du schéma technique pour Airflow..."
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE SCHEMA IF NOT EXISTS airflow;"

echo "Création du schéma et des accès pour l'analytics"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE SCHEMA IF NOT EXISTS raw;"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE TABLE IF NOT EXISTS raw.ticketmaster_events (id SERIAL PRIMARY KEY, inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, file_name TEXT, payload JSONB);"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE INDEX idx_ticketmaster_filename ON raw.ticketmaster_events (file_name)";
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE USER ${DBUSER_RO} WITH PASSWORD '${PASSWORD_RO}';"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "CREATE ROLE analyst_group;"
docker exec postgres_db psql -U ${DBUSER_RW} -d ${DBNAME} -c "GRANT analyst_group TO ${DBUSER};"

# Lancement du reste de l'infrastructure
echo "Lancement du reste de l'infrastructure (Airflow, Garage...)"
docker compose up -d

echo "Initialisation des variables Airflow..."
docker exec airflow_scheduler airflow variables set last_events_git_sha "initial_sync"

# Sauvegarde de sécurité du .env (seulement si le .env n'est pas déjà corrompu)
cp .env .env.last_run

until [ "$(docker ps -a -q -f name=garage_datalake)" ]; do
    echo "Le conteneur n'est pas encore créé... (téléchargement des images ?)"
    sleep 5
done

echo "Attente du démarrage de Garage..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' garage_datalake 2>/dev/null)" == "healthy" ]; do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' garage_datalake 2>/dev/null || echo "initialisation")
  echo "Statut actuel : $STATUS..."
  sleep 2
done

echo "Garage est prêt!"

echo "Configuration du Layout Garage..."

# Récupération de l'ID du nœud
NODE_ID=$(docker exec garage_datalake /garage status | grep "127.0.0.1:3901" | awk '{print $1}')

if [ -z "$NODE_ID" ]; then
    echo "Erreur : Impossible de récupérer l'ID du nœud Garage."
    exit 1
fi

echo "   -> ID du nœud détecté : $NODE_ID"

# Assignation de la capacité (10G dans la zone-france)
docker exec garage_datalake /garage layout assign --capacity 10G --zone zone-france "$NODE_ID"

# Application du layout (Version 1 pour un nouveau cluster)
docker exec garage_datalake /garage layout apply --version 1

echo "Layout appliqué avec succès !"

# Fonction de création de clé
create_garage_key() {
    local NAME=$1
    local KEY_INFO=$(docker exec garage_datalake /garage key create "$NAME" 2>&1)
    
    # Correction des patterns et des colonnes (print $3)
    local ID=$(echo "$KEY_INFO" | grep "Key ID:" | awk '{print $3}')
    local SECRET=$(echo "$KEY_INFO" | grep "Secret key:" | awk '{print $3}')
    
    if [ -z "$ID" ]; then
        echo "Erreur critique : impossible d'extraire l'ID pour $NAME"
        exit 1
    fi

    echo "Clé créée : $NAME (ID: $ID)"
    echo "Nom: $NAME, ID: $ID, Secret: $SECRET" >> garage_dl.txt
    
    eval "${2}=$ID"
    eval "${3}=$SECRET"
}

# Création des différentes clés
# Initialisation du fichier de sauvegarde des clés
echo "--- Identifiants Garage S3 (Générés le $(date)) ---" > garage_dl.txt
create_garage_key "admin-key" "ID_ADMIN" "SEC_ADMIN"
create_garage_key "ingestion-key" "ID_RW" "SEC_RW"
create_garage_key "lambda-key" "ID_LAMBDA" "SEC_LAMBDA"
create_garage_key "monitoring-key" "ID_RO" "SEC_RO"

# Mise à jour automatique du fichier .env ---
echo "Mise à jour du fichier .env..."
# Utilisation de sed pour remplacer les valeurs. 
sed -i "s/^KEY_ID_DL_RW=.*/KEY_ID_DL_RW=$ID_RW/" .env
sed -i "s/^SECRET_KEY_DL_RW=.*/SECRET_KEY_DL_RW=$SEC_RW/" .env
sed -i "s/^KEY_ID_DL_RO=.*/KEY_ID_DL_RO=$ID_RO/" .env
sed -i "s/^SECRET_KEY_DL_RO=.*/SECRET_KEY_DL_RO=$SEC_RO/" .env
sed -i "s/^KEY_ID_LAMBDA=.*/KEY_ID_LAMBDA=$ID_LAMBDA/" .env
sed -i "s/^SECRET_KEY_LAMBDA=.*/SECRET_KEY_LAMBDA=$SEC_LAMBDA/" .env

# Création des buckets et permissions
echo "Création des buckets..."
LISTE_BUCKETS=("zone-config" "zone-brutes" "zone-propres" "zone-enrichies" "zone-tests" "zone-maintenance")

for BUCKET in "${LISTE_BUCKETS[@]}"; do
    docker exec garage_datalake /garage bucket create "$BUCKET"
    docker exec garage_datalake /garage bucket allow "$BUCKET" --read --write --owner --key admin-key
    docker exec garage_datalake /garage bucket allow "$BUCKET" --read --write --key ingestion-key
done

# Lambda : RO sur presque tout + RW sur tests
for BUCKET in "zone-config" "zone-brutes" "zone-propres" "zone-enrichies" "zone-maintenance"; do
    docker exec garage_datalake /garage bucket allow "$BUCKET" --read --key lambda-key
done
docker exec garage_datalake /garage bucket allow zone-tests --read --write --key lambda-key

# Monitoring : RO
for BUCKET in "zone-config" "zone-brutes" "zone-propres" "zone-enrichies"; do
    docker exec garage_datalake /garage bucket allow "$BUCKET" --read --key monitoring-key
done

echo "Mise à jour des conteneurs avec les nouveaux identifiants..."
docker compose up -d

echo "Infrastructure prête !"