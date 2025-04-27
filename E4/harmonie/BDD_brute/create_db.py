# from models import Auteur, Partition, HBM, Evenement, SessionLocal
from models import Auteur, Partition, AssAuteurPartition, Evenement, SessionLocal
from datetime import date, datetime
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, create_engine, ForeignKey, Table, MetaData
import csv
from crud import create_event, create_partition, create_auteur, create_asso_auteur_partition

session = SessionLocal()
# Exécution du script princpal models.py
with open("models.py") as m:
    code = m.read()
exec(code)         

# Insertion du csv évènements dans BDD
def insert_event_to_db(file_path):
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                date_evenement = datetime.strptime(row.get('date_event'), "%d-%m-%Y").date()
                nom_evenement = row.get('nom_event')
                lieu = row.get('lieu')
                type_evenement = row.get('type_event')
                affiche = row.get('affiche')
                create_event(session, date_evenement, nom_evenement, lieu, type_evenement, affiche)    
 
        # Commit des changements
        session.commit()
    except Exception as e:
        # En cas d'erreur, annuler les changements
        session.rollback()
        print(f"Erreur lors de l'importation des données : {e}")
    finally:
        # Fermeture de la session
        session.close()

def insert_scrapy_to_db(file_path):
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                # déclarations des variables
                titre = row.get('titre').upper()
                sous_titre = row.get('sous_titre', None)
                edition = row.get('edition', None)
                collection = row.get('collection', None)
                instrumentation = row.get('instrumentation', None)
                niveau = float(row['niveau']) if row['niveau'] else None
                genre = row.get('genre', None)
                style = row.get('style', None)
                annee_sortie = int(row['annee_sortie']) if row['annee_sortie'] else None
                ISMN = row.get('ISMN', None)
                ref_editeur = row.get('ref_editeur', None)
                duree = row.get('duree', None)
                description = row.get('description', None)
                url = row.get('url', None)
                compositeur_list = row.get('compositeur', None).upper().split(",")
                artiste_list = row.get('artiste', None).upper().split(",")
                arrangeur_list = row.get('arrangeur', None).upper().split(",")
                # partition = insert_partition(session, titre, sous_titre, edition, collection, instrumentation, niveau,
                #                  genre, style, annee_sortie, ISMN, ref_editeur, duree, description, url)

                part_id = create_partition(session, titre, sous_titre, edition, collection, instrumentation, niveau,
                                 genre, style, annee_sortie, ISMN, ref_editeur, duree, description, url).partition_id

                # Boucle sur les compositeurs 
                if compositeur_list and compositeur_list!=[]:                
                    for i in range(len(compositeur_list)):
                        if compositeur_list[i]!='':
                            compositeur = create_auteur(session, compositeur_list[i])
                            compositeur_id = create_auteur(session, compositeur_list[i]).auteur_id
                            # partition.rel_auteur_partition.append(compositeur)
                            create_asso_auteur_partition(session, part_id, compositeur_id, 'compositeur')

                # Boucle sur les artistes 
                if artiste_list and artiste_list!=[]:                
                    for i in range(len(artiste_list)):
                        if artiste_list[i]!='':
                            artiste_id = create_auteur(session, artiste_list[i]).auteur_id
                            create_asso_auteur_partition(session, part_id, artiste_id, 'artiste')

                # Boucle sur les arrangeurs 
                if arrangeur_list and arrangeur_list!=[]:                
                    for i in range(len(arrangeur_list)):
                        if arrangeur_list[i]!='':
                            arrangeur_id = create_auteur(session, arrangeur_list[i]).auteur_id
                            create_asso_auteur_partition(session, part_id, arrangeur_id, 'arrangeur')            

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
event_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/sources/events.csv"
scrapy_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/nouveau.csv"

# Importation des données CSV dans la base de données
insert_event_to_db(event_path)
insert_scrapy_to_db(scrapy_path)