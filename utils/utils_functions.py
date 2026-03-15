# utils_functions.py
"""
Shared Utility Functions - Harmonie Manager 2026.

This module provides common helper functions used across the platform for:
1. Data Normalization: Standardizing identity strings for robust lookups.
2. Rejection Handling: Logging malformed or ambiguous data for manual audit.
"""
import csv
import os
from datetime import datetime
from utils.logger_config import setup_logger, trace_action

logger_name = "Fonction utiliairey"
logger = setup_logger(logger_name)

def normalize_name(nom: str, prenom: str = "") -> str:
    """
    Standardizes names for database searching and deduplication.
    
    Combines first and last names, strips whitespace, and converts to 
    lowercase to create a 'search identity' that is resilient to 
    formatting variations.
    """
    p = prenom.strip() if prenom else ""
    n = nom.strip() if nom else ""

    full = f"{n} {p}".strip().lower()
    return " ".join(full.split())

@trace_action(logger_name)
def write_rejection_log(file_path: str, headers: list, data_row: list):
    """
    Generic CSV rejection logger.
    
    Ensures that any data rejected during synchronization or ingestion 
    is recorded with its context. It automatically manages directory 
    creation and header initialization to prevent data loss.
    
    Args:
        file_path (str): Local path for the rejection file.
        headers (list): CSV column headers (only written if file is new).
        data_row (list): The specific data point that failed processing.
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