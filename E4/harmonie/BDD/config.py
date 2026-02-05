# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print("ℹ️ Info : .env non trouvé, utilisation des variables d'environnement système.")

SQL_DATABASE_URL = os.getenv("SQL_DATABASE_URL")
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
dbhost = os.getenv("DBHOST")
dbname = os.getenv("DBNAME")
dbuser_rw = os.getenv("DBUSER_RW")
password_rw = os.getenv("PASSWORD_RW")
dbuser_ro = os.getenv("DBUSER_RO")
password_ro = os.getenv("PASSWORD_RO")

if not SQL_DATABASE_URL:
    raise ImportError("❌ Erreur critique : SQL_DATABASE_URL est introuvable.")