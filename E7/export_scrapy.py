import os
from azure.storage.filedatalake import DataLakeServiceClient

# Récupérer les variables d'environnement
storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
file_system_name = os.getenv("FILE_SYSTEM_NAME")
local_directory = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/"

# Initialiser le client ADLS
service_client = DataLakeServiceClient(
    account_url=f"https://{storage_account_name}.dfs.core.windows.net",
    credential=storage_account_key
)
file_system_client = service_client.get_file_system_client(file_system=file_system_name)

# Parcourir les fichiers locaux et les télécharger vers ADLS
for root, dirs, files in os.walk(local_directory):
    for file in files:
        local_path = os.path.join(root, file)
        relative_path = os.path.relpath(local_path, local_directory)
        file_client = file_system_client.get_file_client(relative_path)

        # Télécharger le fichier
        with open(local_path, "rb") as file_data:
            file_client.upload_data(file_data, overwrite=True)

print("Téléchargement terminé.")