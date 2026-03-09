# S3_utils.py
"""
S3 Data Lake Orchestration Service.

This module acts as the universal bridge between the application services 
and the Garage S3 Object Storage. It manages data transfers across all 
Medallion zones (Bronze, Silver, Gold, Config).

Key Operational Features:
1. Garage v0.9 Optimization: Forces 'path-style' addressing and S3v4 
   signatures for maximum compatibility.
2. Governance Metadata: Systematically attaches lineage tags (source, step, 
   dag) to every object during upload.
3. Stream Integration: Enables direct I/O between S3 and Pandas/JSON 
   without local temporary files.
4. Lifecycle Management: Provides generic 'move' operations for 
   landing-to-archive transitions.
"""
import os
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import mimetypes
import pandas as pd

from utils.logger_config import trace_action, setup_logger
from config.config import SQL_DATABASE_URL, KEY_ID_DL_RW, SECRET_KEY_DL_RW, DL_ENDPOINT, DL_REGION

logger_name = "E7 - Communications S3"
logger = setup_logger(logger_name)

def get_s3_client():
    """
    Initializes a Read-Write S3 client with Garage-specific configurations.

    Crucially configures 'addressing_style' as 'path' to accommodate the 
    Garage v0.9 backend requirements.
    """
    return boto3.client(
        's3',
        endpoint_url=DL_ENDPOINT,
        aws_access_key_id=KEY_ID_DL_RW,
        aws_secret_access_key=SECRET_KEY_DL_RW,
        region_name=DL_REGION,
        use_ssl=False,
        # Configuration vitale pour Garage v0.9
        config=Config(
            s3={'addressing_style': 'path'},
            signature_version='s3v4'
        )
    )

@trace_action(logger_name)
def upload_file(local_path, bucket, s3_path=None, metadata=None):
    """
    Delivers a local file to the Data Lake with automatic MIME detection.

    Args:
        local_path (str): Path to the source file on disk.
        bucket (str): Target S3 bucket name.
        s3_path (str, optional): Destination key. Defaults to local filename.
        metadata (dict, optional): Custom tags for lineage and governance.
    """
    s3 = get_s3_client()
    
    # Si s3_path n'est pas précisé, on garde le nom du fichier local
    if s3_path is None:
        s3_path = os.path.basename(local_path)
    
    # Détection du type de fichier (ex: text/csv)
    content_type, _ = mimetypes.guess_type(local_path)
    content_type = content_type or 'application/octet-stream'
    
    # Préparation des arguments d'upload
    extra_args = {'ContentType': content_type}
    if metadata:
        extra_args['Metadata'] = metadata

    try:
        s3.upload_file(local_path, bucket, s3_path, ExtraArgs=extra_args)
        logger.info(f"Fichier {local_path} uploadé vers {bucket}/{s3_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de {local_path} : {e}")
        return False

# exemple d'utilisation de metadata:
# upload_file(..., metadata={'source': 'API_Infoconcert', 'step': 'bronze'})

@trace_action(logger_name)
def download_file(bucket, s3_path, local_path):
    """
    Downloads an object from the Data Lake to a local filesystem path.

    Used primarily for scripts requiring local file manipulation before 
    processing. Ensures that the target local directory exists before 
    starting the transfer.

    Args:
        bucket (str): Source S3 bucket.
        s3_path (str): The object key in the Data Lake.
        local_path (str): Destination path on the local machine.
    """
    s3 = get_s3_client()
    
    # Créer le dossier local s'il existe dans le chemin
    directory = os.path.dirname(local_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    try:
        s3.download_file(bucket, s3_path, local_path)
        logger.info(f"Fichier {s3_path} téléchargé vers {local_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {s3_path} : {e}")
        return False

@trace_action(logger_name)
def upload_bytes(data, bucket, s3_path, metadata=None):
    """
    Upload des données brutes (bytes) directement vers S3.
    Idéal pour les flux Git -> S3 sans fichier local.
    """
    s3 = get_s3_client()
    extra_args = {'ContentType': 'text/csv'}
    if metadata:
        extra_args['Metadata'] = metadata

    try:
        s3.put_object(
            Bucket=bucket, 
            Key=s3_path, 
            Body=data, 
            **extra_args
        )
        logger.info(f"Données uploadées vers {bucket}/{s3_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'upload vers {s3_path} : {e}")
        return False

def handle_path(input_path):
    """
    Vérifie si le chemin est local ou S3. 
    Si S3, télécharge le fichier dans /tmp et renvoie le nouveau chemin.
    """
    if input_path.startswith("s3://"):
        # On découpe s3://bucket/key
        parts = input_path.replace("s3://", "").split("/", 1)
        bucket, key = parts[0], parts[1]
        
        # Le dossier /tmp est universel sous Linux (Docker)
        local_tmp = f"/tmp/{os.path.basename(key)}"
        
        if download_file(bucket, key, local_tmp):
            return local_tmp
        else:
            raise Exception(f"Échec du téléchargement S3 pour {input_path}")
            
    return input_path

@trace_action(logger_name)
def read_csv_from_datalake(bucket, s3_path, **kwargs):
    """
    Direct Stream: S3 to Pandas DataFrame.

    Optimized for analytical workloads. It reads the raw bytes of a CSV 
    file from S3 and streams them into a Pandas DataFrame using a buffer.

    Args:
        bucket (str): Source S3 bucket.
        s3_path (str): Path to the CSV file.
        **kwargs: Additional arguments passed to 'pd.read_csv'.

    Returns:
        pd.DataFrame: The loaded dataset.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket, Key=s3_path)
        df = pd.read_csv(response['Body'], **kwargs)
        logger.info(f"CSV {s3_path} lu avec succès depuis le bucket {bucket}")
        return df
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du CSV {s3_path} : {e}")
        return None

@trace_action(logger_name)
def get_json_from_s3(bucket_name, s3_key):
    """
    Direct Stream: S3 to Python Dictionary.

    Retrieves a JSON object and parses it directly into memory. 
    Ideal for processing Ticketmaster API responses stored in the 
    Bronze zone without intermediate disk writes.

    Returns:
        dict: Parsed JSON content or None if an error occurs.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket_name,Key=s3_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except s3.exceptions.NoSuchKey:
        logger.error(f"Le fichier {s3_key} n'existe pas")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture S3 ({s3_key}): {e}")
    return None

@trace_action(logger_name)
def move_s3_object(bucket_name, source_key, source_prefix, target_prefix):
    """
    Generic object relocation service (Copy-then-Delete pattern).
    
    Facilitates the transition of files between Landing and Archive zones 
    to prevent duplicate processing in daily batches.
    """
    s3 = get_s3_client()
    target_key = source_key.replace(source_prefix, target_prefix, 1)

    try:
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': source_key},
            Key=target_key
        )

        s3.delete_object(Bucket=bucket_name, Key=source_key)

        return target_key
    except Exception as e:
        logger.error(f"Erreur move_s3_object: {e}")
        raise

if __name__ == "__main__":
    # Test du download
    success = download_file(
        bucket="zone-config",
        s3_path="backups/data_catalog_v1.json",
        local_path="downloads/restored_catalog.json"
    )
    if success:
        print("Le fichier est bien revenu du Data Lake !")