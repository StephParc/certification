# S3_utils.py
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import mimetypes
import pandas as pd
from dotenv import load_dotenv
from utils.logger_config import trace_action, setup_logger

logger_name = "E7 - Communications S3"
logger = setup_logger(logger_name)

load_dotenv()

def get_s3_client():
    """Initialise le client S3 avec les droits d'écriture (RW)"""
    return boto3.client(
        's3',
        endpoint_url=os.getenv("DL_ENDPOINT"),
        aws_access_key_id=os.getenv("KEY_ID_DL_RW"),
        aws_secret_access_key=os.getenv("SECRET_KEY_DL_RW"),
        region_name="garage",
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
    Upload un fichier sur le Data Lake avec détection de type et métadonnées.
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
    Télécharge un fichier du Data Lake vers le disque local.
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
def read_csv_from_datalake(bucket, s3_path):
    """
    Lit un fichier CSV depuis le datalake et retourne un DataFrame Pandas.
    file_key: le chemin du fichier dans le bucket (ex: 'raw/partitions.csv')
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket, Key=s3_path)
        df = pd.read_csv(response['Body'])
        logger.info(f"CSV {s3_path} lu avec succès depuis le bucket {bucket}")
        return df
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du CSV {s3_path} : {e}")
        return None

if __name__ == "__main__":
    # Test du download
    success = download_file(
        bucket="zone-config",
        s3_path="backups/data_catalog_v1.json",
        local_path="downloads/restored_catalog.json"
    )
    if success:
        print("Le fichier est bien revenu du Data Lake !")