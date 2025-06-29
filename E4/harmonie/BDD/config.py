# config.py
import os
from dotenv import load_dotenv

load_dotenv()

SQL_DATABASE_URL = os.getenv("SQL_DATABASE_URL")
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")