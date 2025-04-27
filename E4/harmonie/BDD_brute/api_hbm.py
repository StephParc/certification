from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer, String, Float, MetaData, create_engine, and_
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from models import Base
from models import Auteur, Partition, AssAuteurPartition, Evenement, HBM, AssEvenementHbm

import os
from dotenv import load_dotenv

# Spécifiez le chemin vers votre fichier .env
env_path = os.path.join(os.path.dirname(__file__),'.env')
# Chargez les variables d'environnement depuis le fichier .env
load_dotenv(dotenv_path=env_path)


app = FastAPI()

# def session_open():
#     # engine = create_engine('sqlite:///mydatabase.db', connect_args={"check_same_thread": False})   
#     # Session = sessionmaker(bind=engine)
#     # session = Session()
# ########################### automatisation avec le script_automatise et le .env

#     # Maintenant, vous pouvez accéder aux variables d'environnement comme d'habitude
#     DATABASE_URL = os.getenv('DATABASE_URL')
#     engine = create_engine(DATABASE_URL)
# ########################### fin automatisation

#     Session = sessionmaker(bind=engine) # permet de gérer les transaction (ajout et modification et suppression de données)
#     session = Session()

#     return session
DATABASE_URL = os.getenv('DATABASE_URL')

def session_open():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# affichage des formations simplon dont l'intitulé de formation contient intitule
@app.get("/formation_simplon_from_intitule")
def get_formation_simplon(intitule:str):
    session = session_open()
    intitule_test = f"%{intitule}%"
    match_intitule = session.query(FormationsSimplon).filter(FormationsSimplon.intitule_formation.ilike(intitule_test)).all()
    if match_intitule:
        session.close()
        return match_intitule
    else:
        session.close()
        return "pas trouvé"