# harvester.py
"""
Governance Metadata Harvester - Harmonie Manager 2026.

This module acts as the central observability engine for the entire platform. 
It performs deep metadata extraction across all architectural layers to 
generate a unified 'Data Catalog'.

Core Capabilities:
1. SQL Metadata: Introspects PostgreSQL schemas, tables, columns, and 
   constraints (PK/FK).
2. Data Lake Inventory: Scans S3 (Garage) buckets and extracts custom 
   governance tags (source, step, dag).
3. Lineage Extraction: Parses dbt manifests to map data transformations 
   and Airflow DAGs for task dependencies.
4. System Observability: Captures server health metrics (CPU, RAM, Disk).
"""
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
import psutil
import platform
import re

from utils.logger_config import trace_action, setup_logger
from utils.S3_utils import upload_file

logger_name = "E7-Catalogue"
logger = setup_logger(logger_name)

load_dotenv()

@trace_action(logger_name)
def catalogue_BDD():
    """
    Performs deep introspection of the PostgreSQL environment.
    
    It iterates through all non-system databases to extract:
    - Table types (Base table vs View).
    - Column details (Types, Nullability, Descriptions).
    - Relational constraints (Primary and Foreign Keys).
    - Storage metrics (Row counts and byte sizes).
    """
    all_results = []

    try:
        base_conn = psycopg2.connect(
            host=os.getenv('DBHOST'),
            port=os.getenv('DBPORT', 5433),
            database=os.getenv('DBNAME'),
            user=os.getenv('DBUSER_RW'),
            password=os.getenv('PASSWORD_RW'),
            options="-c client_encoding=utf8"
        )
        cur_list = base_conn.cursor()
        cur_list.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';")
        databases = [row[0] for row in cur_list.fetchall()]
        cur_list.close()
        base_conn.close()

        logger.info(f"Bases de données détectées: {databases}")
    except Exception as e:
        logger.error(f"Impossible de lister les bases: {e}")

    for db in databases:
        try:
            conn = psycopg2.connect(
                host=os.getenv('DBHOST'),
                port=os.getenv('DBPORT', 5433),
                database=db,
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
                pgc.reltuples::bigint AS nb_lignes,
                pg_total_relation_size(pgc.oid) AS taille_octets,
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
                pgc.reltuples, pgc.oid, 
                c.column_name, c.udt_name, c.is_nullable, c.ordinal_position, pgd.description
            ORDER BY t.table_name, c.ordinal_position;
            """
            
            cur.execute(query)
            all_results.extend(cur.fetchall())
            
            cur.close()
            conn.close()
            logger.info(f"Métadonnées extraites pour la base: {db}")
        
        # except psycopg2.OperationalError as e:
        #     logger.error(f"Impossible de se connecter à la base SQL : {e}")
        #     return []
        except Exception as e:
            # 1. On nettoie le message pour éviter le bug de décodage '0xe9'
            error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
            
            # 2. On loggue l'erreur proprement via ton logger configuré
            logger.error(f"Erreur lors du catalogage BDD : {error_msg}")
            return []
    return all_results

@trace_action(logger_name)
def catalogue_DL():
    """
    Inventory service for the S3 Data Lake (Bronze/Silver/Gold/Config).
    
    Beyond basic file listing, it retrieves custom user-defined metadata 
    (tags) to track data provenance and the specific Airflow DAGs 
    responsible for each object.
    """
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

                    try:
                        head = s3.head_object(Bucket=bucket_name, Key=key)
                        # Les métadonnées utilisateur sont dans 'Metadata'
                        meta = head.get('Metadata', {})
                    except:
                        meta = {}

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
                        "is_folder": key.endswith('/'),
                        "source": meta.get('source', 'Inconnue'),
                        "step": meta.get('step', 'N/A'),
                        "dag": meta.get('dag', 'Inconnue'), 
                        "destination": meta.get('destination', 'N/A')
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

    storage_summary = {}
    for bucket in buckets:
        objs = [o for o in catalog_s3 if o.get('bucket') == bucket]
        total_size = sum(o.get('size_ko', 0) for o in objs)
        storage_summary[bucket] = {
            "total_size_ko": round(total_size, 2),
            "objet_count": len(obj)
        }
            
    return {
        "items": catalog_s3,
        "summary": storage_summary
    }

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
def get_system_stats():
    """Récupère l'état de santé du serveur de données"""
    return {
        "server_name": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_usage_pct": psutil.cpu_percent(interval=1),
        "ram_usage_pct": psutil.virtual_memory().percent,
        "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        "status": "Healthy" if psutil.cpu_percent() < 90 else "Warning"
    }

@trace_action(logger_name)
def get_dbt_lineage():
    """
    Parses the dbt 'manifest.json' to reconstruct the data lineage graph.
    Identifies nodes (models/snapshots) and their edges (dependencies) 
    to visualize the transformation flow.
    """
    # Chemin vers le manifest de ton projet 'musicshop'
    manifest_path = "harmonie_dbt/target/manifest.json"
    
    lineage_nodes = {}
    lineage_edges = []
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
                nodes = manifest.get('nodes', {})
                
                for node_id, node_data in nodes.items():
                    # On filtre pour ne garder que les modèles et snapshots de ton projet
                    if node_data['resource_type'] in ['model', 'snapshot']:
                        node_name = node_data['name']
                        materialized = node_data['config']['materialized']
                        
                        # On stocke l'info du noeud (pour sa couleur dans Streamlit)
                        lineage_nodes[node_name] = materialized
                        
                        # On récupère les parents (depends_on)
                        depends_on_nodes = node_data.get('depends_on', {}).get('nodes', [])
                        
                        for parent_id in depends_on_nodes:
                            # On ne garde que le nom propre (pas le type de ressource)
                            parent_name = parent_id.split('.')[-1]
                            # On crée le lien
                            lineage_edges.append({"from": parent_name, "to": node_name})
                            
            logger.info(f"Lignage dynamique dbt extrait ({len(lineage_nodes)} noeuds, {len(lineage_edges)} liens)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du manifest dbt : {e}")
    else:
        logger.warning(f"Manifest dbt introuvable ({manifest_path}). Lance 'dbt build'.")
        
    return {"nodes": lineage_nodes, "edges": lineage_edges}

@trace_action(logger_name)
def get_airflow_dags_from_code():
    """
    Static Analysis Engine for Airflow Orchestration.
    
    Reads DAG Python files without executing them to extract:
    - DAG and Task IDs.
    - Execution logic and task dependencies (via '>>' operator parsing).
    """
    dags_folder = "dags"
    dags_logic = []

    if not os.path.exists(dags_folder):
        return []

    for file in os.listdir(dags_folder):
        if file.endswith(".py") and file != "__init__.py":
            path = os.path.join(dags_folder, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

                # 1. Extraction ID du DAG
                dag_id_match = re.search(r'dag_id=["\']([^"\']+)["\']', content)
                # Si pas trouvé dans le code, on prend le nom du DAG dans le 'with DAG(...) as name'
                if not dag_id_match:
                    dag_id_match = re.search(r'DAG\(\s*["\']([^"\']+)["\']', content)
                
                dag_id = dag_id_match.group(1) if dag_id_match else file

                # 2. Mapping Variable -> Task_ID 
                # On utilise re.DOTALL pour gérer les définitions sur plusieurs lignes
                task_map = {}
                # Cherche : ma_var = Operator( ... task_id='mon_id' ... )
                task_patterns = re.findall(r'(\w+)\s*=\s*[^=]*?task_id=["\']([^"\']+)["\']', content, re.DOTALL)
                for var_name, t_id in task_patterns:
                    task_map[var_name] = t_id

                # 3. Extraction des chaînes complexes : check >> t1 >> t2
                edges = []
                # On cherche toutes les lignes contenant >>
                for line in content.split('\n'):
                    if '>>' in line:
                        # On sépare les éléments de la chaîne
                        parts = [p.strip() for p in line.split('>>')]
                        for i in range(len(parts) - 1):
                            start_var = parts[i]
                            end_var = parts[i+1]
                            # On ne crée le lien que si on connaît les IDs réels
                            if start_var in task_map and end_var in task_map:
                                edges.append({"from": task_map[start_var], "to": task_map[end_var]})

                dags_logic.append({
                    "file": file,
                    "dag_id": dag_id,
                    "tasks": list(task_map.values()), # On ne prend que les IDs réels
                    "dependencies": edges
                })
    return dags_logic

@trace_action(logger_name)
def catalogue_export():
    """
    The Orchestrator of Governance.
    
    Aggregates all metadata (SQL, NoSQL, S3, dbt, Airflow, System) into 
    a single 'data_catalog.json' and secures it in the 'zone-config' 
    S3 bucket for auditing and Streamlit visualization.
    """
    dbt_data = get_dbt_lineage()
    
    data = {
        "export_date": datetime.now().isoformat(),
        "system_health": get_system_stats(),
        "dbt_lineage": get_dbt_lineage(),
        "dbt_nodes": dbt_data['nodes'],  
        "dbt_edges": dbt_data['edges'],
        "airflow_static_analysis": get_airflow_dags_from_code(),
        "relational_db": catalogue_BDD(),
        "datalake": catalogue_DL(),
        "nosql_db": catalogue_Mongo(),
        "governance_reference": "access_control.json"
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
    catalogue_export()