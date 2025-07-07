# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__),'.env')
load_dotenv(dotenv_path=env_path)

def get_engine():
    SQL_DATABASE_URL = os.getenv('SQL_DATABASE_URL')
    engine = create_engine(SQL_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    return engine

def sql_connect():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session_sql():
    SessionLocal = sql_connect()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
