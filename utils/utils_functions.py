# utils_functions.py
import csv
import os
from datetime import datetime
from utils.logger_config import setup_logger, trace_action

logger_name = "Fonction utiliairey"
logger = setup_logger(logger_name)

def normalize_name(nom: str, prenom: str = "") -> str:
    """Combine, nettoie et met en minuscule pour une recherche fiable."""
    p = prenom.strip() if prenom else ""
    n = nom.strip() if nom else ""

    full = f"{n} {p}".strip().lower()
    return " ".join(full.split())

@trace_action(logger_name)
def write_rejection_log(file_path: str, headers: list, data_row: list):
    """
    Fonction générique pour écrire une ligne dans un fichier de rejet CSV.
    Gère la création de dossiers et l'écriture de l'en-tête si nécessaire.
    """
    try:
        # 1. Gestion du répertoire (évite l'erreur du dossier vide)
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # 2. Vérification de l'état du fichier
        file_exists = os.path.isfile(file_path)
        is_empty = os.stat(file_path).st_size == 0 if file_exists else True
        
        # 3. Écriture
        with open(file_path, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';') # Point-virgule souvent mieux pour le Datalake
            
            # Écrit l'en-tête uniquement si le fichier est neuf/vide
            if is_empty:
                writer.writerow(headers)
            
            writer.writerow(data_row)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans {file_path} : {e}")