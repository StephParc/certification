# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

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

SQL_DATABASE_URL = os.getenv("SQL_DATABASE_URL")
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
DBHOST = os.getenv("DBHOST")
DBNAME = os.getenv("DBNAME")
DBPORT = os.getenv("DBPORT")
DBUSER_RW = os.getenv("DBUSER_RW")
PASSWORD_RW = os.getenv("PASSWORD_RW")
DBUSER_RO = os.getenv("DBUSER_RO")
PASSWORD_RO = os.getenv("PASSWORD_RO")
DL_ENDPOINT=os.getenv("DL_ENDPOINT")
KEY_ID_DL_RW=os.getenv("KEY_ID_DL_RW")
SECRET_KEY_DL_RW=os.getenv("SECRET_KEY_DL_RW")
DL_REGION=os.getenv("DL_REGION")
REJET_AUTEURS_PATH = LOGS_BASE_PATH / "api_musicbrainz/rejets_auteurs.csv"
REJET_IMPORT_PATH = LOGS_BASE_PATH / "imports_global/rejets_scrapy.csv"
REJET_INSTRUMENTS_PATH = LOGS_BASE_PATH / "sync/instruments_a_completer.csv"
USER_LOG_PATH = LOGS_BASE_PATH / "sync/credentials_temp.csv"
RECONCILIATION_PARTITIONS_PATH = LOGS_BASE_PATH / "sync/partitions_a_reconcilier.csv"
TICKETMASTER_CONSUMER_KEY = os.getenv("TICKETMASTER_CONSUMER_KEY")
TICKETMASTER_CONSUMER_SECRET = os.getenv("TICKETMASTER_CONSUMER_SECRET")
SQL_TICKETMASTER_URL = os.getenv("SQL_TICKETMASTER_URL")
SQL_MUSICSHOP_URL = os.getenv("SQL_MUSICSHOP_URL")

if not SQL_DATABASE_URL:
    raise ImportError("Erreur critique : SQL_DATABASE_URL est introuvable.")
