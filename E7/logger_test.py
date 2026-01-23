import boto3
import os
from utils.logger_config import trace_action, setup_logger


# Configuration (toujours les mêmes)
ACCESS_KEY = "admin_hbm"
SECRET_KEY = "hbm_password_2024"
MINIO_URL = "http://localhost:9000"

logger = setup_logger("E7-DataLake")

@trace_action
def upload_concert_data():
    s3 = boto3.client("s3", endpoint_url=MINIO_URL, 
                          aws_access_key_id=ACCESS_KEY, 
                          aws_secret_access_key=SECRET_KEY)

    # Chemin relatif : on remonte (..) vers Certification, puis on descend dans E5...
    # Note : Vérifie bien le nom exact du fichier !
    path_local = "../E5/infoconcert/infoconcert/2026-01-13-infoconcert.csv"
    
    # On vérifie si le fichier existe avant de tenter l'upload
    if os.path.exists(path_local):
        print(f"🔍 Fichier trouvé : {path_local}")
        s3.upload_file(path_local, "test-manuel", "2026-01-13-infoconcert.csv")
        print("✅ Transfert réussi vers le bucket 'test-manuel' !")
    else:
        print(f"❌ Erreur : Le fichier est introuvable au chemin {os.path.abspath(path_local)}")

if __name__ == "__main__":
    upload_concert_data()