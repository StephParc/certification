# database.py
"""
Database Connection & Session Management.

Provides the infrastructure for both SQL (SQLAlchemy) and NoSQL 
(PyMongo) database interactions.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pymongo import MongoClient

from config.config import SQL_DATABASE_URL, MONGO_DATABASE_URL, MONGO_DBNAME

def get_engine():
    ## Pour une BDD SQLite: 
    # SQL_DATABASE_URL = os.getenv('SQL_DATABASE_URL')
    # engine = create_engine(SQL_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

    # Pour une BDD PostgreSQL:
    engine = create_engine(SQL_DATABASE_URL, echo=True)
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

def get_mongo_client():
    """
    Returns a client to the configured MongoDB database.
    """
    return MongoClient(MONGO_DATABASE_URL)

def get_mongo_db():
    client = get_mongo_client()
    return client[MONGO_DBNAME]