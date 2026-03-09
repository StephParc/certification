# config.py
"""
Centralized Configuration Module.

This module handles environment variable loading and provides a unified 
interface for all system settings, including database connections (SQL/Mongo), 
security parameters, S3 storage (Garage), and logging paths.

It automatically initializes the required directory structure for logs 
and rejects during the first import.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Path resolution for .env discovery
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print("Info : .env non trouvé, utilisation des variables d'environnement système.")

LOGS_BASE_PATH = BASE_DIR / os.getenv("LOGS_ROOT_DIR", "logs/rejets")
for path in [
    LOGS_BASE_PATH / "api_musicbrainz",
    LOGS_BASE_PATH / "imports_global",
    LOGS_BASE_PATH / "sync"]:
    path.mkdir(parents=True, exist_ok=True)

# --- General System Settings ---
PYTHONPATH = os.getenv("PYTHONPATH")

# --- PostgreSQL Database Settings ---
DBHOST = os.getenv("DBHOST")
DBNAME = os.getenv("DBNAME")
DBPORT = os.getenv("DBPORT")
DBUSER_RW = os.getenv("DBUSER_RW")
PASSWORD_RW = os.getenv("PASSWORD_RW")
DBUSER_RO = os.getenv("DBUSER_RO")
PASSWORD_RO = os.getenv("PASSWORD_RO")
SQL_DATABASE_URL = os.getenv("SQL_DATABASE_URL")

# --- Specialized Databases (DHW & Airflow) ---
DBNAME_AIRFLOW = os.getenv("DBNAME_AIRFLOW")
DBNAME_TICKETMASTER = os.getenv("DBNAME_TICKETMASTER")
DBNAME_MUSICSHOP = os.getenv("DBNAME_MUSICSHOP")
SQL_TICKETMASTER_URL = os.getenv("SQL_TICKETMASTER_URL")
SQL_MUSICSHOP_URL = os.getenv("SQL_MUSICSHOP_URL")

# --- MongoDB Settings ---
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# --- API Security & Authentication ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# --- Data Lake Settings (Garage S3) ---
DL_ENDPOINT=os.getenv("DL_ENDPOINT")
KEY_ID_DL_RW=os.getenv("KEY_ID_DL_RW")
SECRET_KEY_DL_RW=os.getenv("SECRET_KEY_DL_RW")
DL_REGION=os.getenv("DL_REGION")
REJET_AUTEURS_PATH = LOGS_BASE_PATH / "api_musicbrainz/rejets_auteurs.csv"
REJET_IMPORT_PATH = LOGS_BASE_PATH / "imports_global/rejets_scrapy.csv"
REJET_INSTRUMENTS_PATH = LOGS_BASE_PATH / "sync/instruments_a_completer.csv"
USER_LOG_PATH = LOGS_BASE_PATH / "sync/credentials_temp.csv"
RECONCILIATION_PARTITIONS_PATH = LOGS_BASE_PATH / "sync/partitions_a_reconcilier.csv"

# --- Third-party Services (TicketMaster & Discord) ---
TICKETMASTER_CONSUMER_KEY = os.getenv("TICKETMASTER_CONSUMER_KEY")
TICKETMASTER_CONSUMER_SECRET = os.getenv("TICKETMASTER_CONSUMER_SECRET")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not SQL_DATABASE_URL:
    raise ImportError("Erreur critique : SQL_DATABASE_URL est introuvable.")

# --- Airflow & Infrastructure Settings ---
AIRFLOW_DATABASE_URL = os.getenv("AIRFLOW_DATABASE_URL")
AIRFLOW_EXECUTOR = os.getenv("AIRFLOW_EXECUTOR")
AIRFLOW_ADMIN_USER = os.getenv("AIRFLOW_ADMIN_USER")
AIRFLOW_ADMIN_PASSWORD = os.getenv("AIRFLOW_ADMIN_PASSWORD")
AIRFLOW_FIRSTNAME = os.getenv("AIRFLOW_FIRSTNAME")
AIRFLOW_LASTNAME = os.getenv("AIRFLOW_LASTNAME")
AIRFLOW_EMAIL = os.getenv("AIRFLOW_EMAIL")
AIRFLOW_UID = os.getenv("AIRFLOW_UID")
AIRFLOW_WEBSERVER_URL = os.getenv("AIRFLOW_WEBSERVER_URL")

# --- External Sync URLs ---
GIT_RAW_URL = os.getenv("GIT_RAW_URL")
GIT_API_URL = os.getenv("GIT_API_URL")

# --- Network & Tunneling (Ngrok) ---
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
NGROK_USER = os.getenv("NGROK_USER")
NGROK_PASSWORD = os.getenv("NGROK_PASSWORD")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")
