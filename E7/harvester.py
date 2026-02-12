# harvester.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from botocore.client import Config
from pymongo import MongoClient
from datetime import datetime

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger_config import trace_action, setup_logger
from utils.S3_utils import upload_file

# env_path = os.path.join(os.path.dirname(__file__),'../.env')
# load_dotenv(dotenv_path=env_path)

logger_name = "E7-Catalogue"
logger = setup_logger(logger_name)

# Chargement du .env situé dans le dossier parent
# BASE_DIR = Path(__file__).resolve().parent
# load_dotenv(BASE_DIR.parent / ".env")
load_dotenv()

@trace_action(logger_name)
def catalogue_BDD():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DBHOST'),
            port=os.getenv('DBPORT', 5433),
            database=os.getenv('DBNAME'),
            user=os.getenv('DBUSER_RW'),
            password=os.getenv('PASSWORD_RW'),
            options="-c client_encoding=utf8"
        )
        
        # RealDictCursor transforme chaque ligne en dictionnaire Python
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            t.table_catalog AS nom_base,
            t.table_schema AS schema,
            CASE 
                WHEN t.table_type = 'BASE TABLE' THEN 'table'
                WHEN t.table_type = 'VIEW' THEN 'vue'
                ELSE t.table_type
            END AS type_table,
            t.table_name AS nom_table,
            c.column_name AS nom_colonne,
            c.udt_name AS type_data,
            c.is_nullable AS nullable,
            -- Regroupement de toutes les contraintes de la colonne en une seule chaîne
            string_agg(
                CASE 
                    WHEN tc.constraint_type = 'PRIMARY KEY' THEN 'PK'
                    WHEN tc.constraint_type = 'FOREIGN KEY' THEN 'FK'
                    ELSE tc.constraint_type
                END, 
                ' | ' 
                ORDER BY CASE tc.constraint_type
                    WHEN 'PRIMARY KEY' THEN 1
                    WHEN 'FOREIGN KEY' THEN 2
                    WHEN 'UNIQUE' THEN 3
                    ELSE 4
                END
            ) AS contraintes,
            pgd.description AS colonne_description
        FROM information_schema.tables t 
        JOIN information_schema.columns c 
            ON t.table_name = c.table_name 
            AND t.table_schema = c.table_schema
        JOIN pg_class pgc ON pgc.relname = t.table_name
        JOIN pg_namespace pgn ON pgn.oid = pgc.relnamespace AND pgn.nspname = t.table_schema
        LEFT JOIN pg_description pgd 
            ON pgd.objoid = pgc.oid 
            AND pgd.objsubid = c.ordinal_position
        LEFT JOIN information_schema.key_column_usage kcu 
            ON kcu.table_name = c.table_name 
            AND kcu.table_schema = c.table_schema 
            AND kcu.column_name = c.column_name
        LEFT JOIN information_schema.table_constraints tc 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_name = c.table_name
            AND tc.constraint_type <> 'CHECK'
        WHERE t.table_schema NOT IN ('information_schema', 'pg_catalog')
        GROUP BY 
            t.table_catalog, t.table_schema, t.table_type, t.table_name, 
            c.column_name, c.udt_name, c.is_nullable, c.ordinal_position, pgd.description
        ORDER BY t.table_name, c.ordinal_position;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        return results
    
    # except psycopg2.OperationalError as e:
    #     logger.error(f"Impossible de se connecter à la base SQL : {e}")
    #     return []
    except Exception as e:
        # 1. On nettoie le message pour éviter le bug de décodage '0xe9'
        error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
        
        # 2. On loggue l'erreur proprement via ton logger configuré
        logger.error(f"Erreur lors du catalogage BDD : {error_msg}")
        return []

@trace_action(logger_name)
def catalogue_DL():
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv("DL_ENDPOINT"),
        aws_access_key_id=os.getenv("KEY_ID_DL_RO"),
        aws_secret_access_key=os.getenv("SECRET_KEY_DL_RO")
    )

    # Liste des buckets à scanner
    buckets = ["zone-brutes", "zone-propres", "zone-enrichies", "zone-config"]
    catalog_s3 = []

    for bucket_name in buckets:
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if not key.endswith('/'):
                        parts = key.split('/')
                        name = parts[-1]   
                        file_root = "/".join(parts[:-1])
                        file_root = f"{file_root}/" 
                    else:
                        name = None
                        file_root = key
                    
                    catalog_s3.append({
                        "bucket": bucket_name,
                        "file_name": name,
                        "path": file_root,
                        "format": os.path.splitext(key)[1].replace('.', '') or ("folder" if key.endswith('/') else "unknown"),
                        "size_ko": round(obj['Size'] / 1024, 2),
                        "last_modified": obj['LastModified'].isoformat(),
                        "etag": obj['ETag'].replace('"', ''),
                        "is_folder": key.endswith('/')
                    })
            else:
                catalog_s3.append({
                    "bucket": bucket_name,
                    "file_name": None,
                    "format": None,
                    "size_ko": 0,
                    "status": "Empty"
                })

        except Exception as e:
            logger.error(f"Erreur sur le bucket {bucket_name}: {e}")
            
    return catalog_s3

@trace_action(logger_name)
def catalogue_Mongo():
    try:
        client = MongoClient(os.getenv("MONGO_DATABASE_URL"))
        db = client[os.getenv("MONGO_DBNAME")]
        
        mongo_meta = []
        for coll_name in db.list_collection_names():
            coll = db[coll_name]
            # On prend un document pour voir à quoi ressemblent les clés (schéma dynamique)
            sample = coll.find_one()
            keys = [str(k) for k in sample.keys()] if sample else []
            
            mongo_meta.append({
                "collection": coll_name,
                "count": coll.count_documents({}),
                "fields": keys
            })
    except Exception as e:
        logger.error(f"MongoDB non disponible : {e}")
        return []
    return mongo_meta

@trace_action(logger_name)
def catalogue_export():
    """Fonction maîtresse qui assemble et sauvegarde"""
    
    data = {
        "export_date": datetime.now().isoformat(),
        "relational_db": catalogue_BDD(),
        "datalake": catalogue_DL(),
        "nosql_db": catalogue_Mongo(),
        "governance_reference": "access_control.json" # Lien symbolique
    }
    
    # Génération du JSON final
    file_path = "data_catalog.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"Catalogue exporté avec succès dans {file_path}")
    
    try:
        upload_file(
            local_path=file_path,
            bucket="zone-config",
            s3_path="governance/data_catalog.json",
            metadata={"version": datetime.now().strftime("%Y%m%d"), "type": "catalog"}
        )
        logger.info("Catalogue sauvegardé dans Garage (zone-config)")
    except Exception as e:
        logger.error(f"Échec de la sauvegarde S3 : {e}")

    return file_path

if __name__ == "__main__":
    # --- TEST 1 : PostgreSQL ---
    # print("\n--- TEST BDD ---")
    # res_bdd = catalogue_BDD()
    # print(f"Nombre de colonnes cataloguées : {len(res_bdd)}")
    # if res_bdd: print(f"Exemple : {res_bdd[0]['nom_table']} -> {res_bdd[0]['nom_colonne']}")

    # --- TEST 2 : Data Lake (Garage) ---
    # print("\n--- TEST DL ---")
    # res_dl = catalogue_DL()
    # print(f"Nombre d'objets trouvés : {len(res_dl)}")
    # for item in res_dl:
    #     size = item.get('size_ko', f"{item['size_ko']} bytes")
    #     print(f"- {item['bucket']}: {item['file_name']} ({size})")

    # --- TEST 3 : MongoDB ---
    # print("\n--- TEST MONGO ---")
    # res_mongo = catalogue_Mongo()
    # print(res_mongo)

    # --- EXPORT COMPLET ---
    catalogue_export()