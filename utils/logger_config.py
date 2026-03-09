#logger_config.py
"""
Centralized Logging and Audit Service - Harmonie Manager 2026.

This module standardizes how the application records its operational 
history. It ensures that every script, from data ingestion to API 
requests, leaves a reliable audit trail.

Key Features:
1. Unified Sink: Directs all logs to a single 'certification.log' file 
   at the project root for easy analysis.
2. Dual Output: Simultaneous logging to the file and the system console 
   to facilitate real-time debugging.
3. Automated Function Auditing: Provides the '@trace_action' decorator to 
   capture function lifecycle (Start, End, and Exceptions).
"""
import logging
import functools
import os

# Global path setup for the central log file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "certification.log")

def setup_logger(name):
    """
    Creates and configures a named logger instance.

    Configures a logger with both File and Stream (Console) handlers. 
    It applies a standard format: timestamp - name - level - message.

    Args:
        name (str): The name of the module or service (e.g., 'E4 - API').

    Returns:
        logging.Logger: A configured logger ready for use.
    """
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

def trace_action(logger_name="Audit-Global"):
    """
    Audit Decorator for automated function tracking.

    Wraps a function to automatically log its execution parameters at 
    the start, its success status at the end, and any traceback in case 
     of an error. This is a key asset for 
    troubleshooting complex ETL pipelines.

    Args:
        logger_name (str): The name of the logger to use for the audit 
                           trail. Defaults to 'Audit-Global'.
    """
    def decorateur(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            logger.info(f"START - {func.__name__} | Args: {args} | kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"END   - {func.__name__} | Success")
                return result
            except Exception as e:
                logger.error(f"ERROR - {func.__name__} | Exception: {str(e)}")
                raise e
        return wrapper
    return decorateur