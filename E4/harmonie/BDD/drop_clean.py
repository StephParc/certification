# drop_clean.py
# fichier utilitaire pour nettoyer la BDD pendant la phase de développement
from E4.harmonie.BDD.database import get_engine
from E4.harmonie.BDD.models import Base

if __name__ == "__main__":
    engine = get_engine()
    
    # 1. On supprime tout (SQLAlchemy gère l'ordre)
    print("Suppression des tables...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. On recrée tout avec les nouvelles structures (UUID, etc.)
    print("Création des nouvelles tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Base de données PostgreSQL mise à jour !")