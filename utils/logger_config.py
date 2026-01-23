import logging
import functools
import os

# Configuration globale pour que tous les logs aillent dans le même fichier à la racine
# On utilise un chemin absolu ou relatif par rapport à la racine du projet
LOG_FILE = "certification.log"

def setup_logger(name):
    """Crée un logger nommé qui écrit dans certification.log et dans la console."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Handler Fichier
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        
        # Handler Console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger

# On crée un logger par défaut pour le décorateur
default_logger = setup_logger("Audit-Global")

def trace_action(func):
    """Décorateur pour logger automatiquement le début, la fin et les erreurs d'une fonction."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        default_logger.info(f"START - {func.__name__} | Args: {args}")
        try:
            result = func(*args, **kwargs)
            default_logger.info(f"END   - {func.__name__} | Success")
            return result
        except Exception as e:
            default_logger.error(f"ERROR - {func.__name__} | Exception: {str(e)}")
            raise e
    return wrapper