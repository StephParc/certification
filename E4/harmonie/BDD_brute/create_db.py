from models import Auteur, Partition, HBM, Evenement
from datetime import date
from sqlalchemy.orm import Session
import csv


event_path= "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/sources/events.csv"
# Fonction pour lire le fichier CSV et insérer les données
def import_csv_to_db(file_path):
    # Création d'une session
    session = SessionLocal()

    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                # Création d'un objet Partition
                partition = Partition(
                    titre=row['titre'],
                    sous_titre=row['sous_titre'],
                    edition=row['edition'],
                    collection=row['collection'],
                    instrumentation=row['instrumentation'],
                    niveau=float(row['niveau']) if row['niveau'] else None,
                    genre=row['genre'],
                    style=row['style'],
                    annee_sortie=int(row['annee_sortie']) if row['annee_sortie'] else None,
                    partie_euro=row['partie_euro'].lower() == 'true' if row['partie_euro'] else None,
                    ISMN=row['ISMN'],
                    ref_editeur=row['ref_editeur'],
                    duree=row['duree'],
                    description=row['description'],
                    url=row['url'],
                    hbm=row['hbm'].lower() == 'true' if row['hbm'] else None
                )

                # Ajout de l'objet à la session
                session.add(partition)

        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

# Chemin vers le fichier CSV
event_path= "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/sources/events.csv"

# Importation des données CSV dans la base de données
import_csv_to_db(event_path)