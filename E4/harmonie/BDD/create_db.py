# create_db.py
from database import get_session_sql, sql_connect
from datetime import date, datetime
import csv
from crud import create_event, create_partition, create_auteur, create_asso_auteur_partition, create_user_admin
from api_externe import get_api_externe

# session = get_session_sql()
SessionLocal= sql_connect()
session = SessionLocal()

# Exécution du script princpal models.py      
with open("models.py") as m:
    code = m.read()
exec(code)

# Insertion du csv évènements dans BDD
def insert_event_to_db(file_path):
    SessionLocal= sql_connect()
    session = SessionLocal()
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
                sous_titre = row.get('sous_titre')
                edition = row.get('edition')
                collection = row.get('collection')
                instrumentation = row.get('instrumentation')
                niveau = float(row['niveau']) if row['niveau'] else None
                genre = row.get('genre')
                style = row.get('style')
                annee_sortie = int(row['annee_sortie']) if row['annee_sortie'] else None
                ISMN = row.get('ISMN')
                ref_editeur = row.get('ref_editeur')
                duree = row.get('duree')
                description = row.get('description')
                url = row.get('url')
                compositeur_list = row.get('compositeur').split(",")
                artiste_list = row.get('artiste').split(",")
                arrangeur_list = row.get('arrangeur').split(",")
                # partition = insert_partition(session, titre, sous_titre, edition, collection, instrumentation, niveau,
                #                  genre, style, annee_sortie, ISMN, ref_editeur, duree, description, url)

                part_id = create_partition(session, titre, sous_titre, edition, collection, instrumentation, niveau,
                                 genre, style, annee_sortie, ISMN, ref_editeur, duree, description, url).partition_id

                # Boucle sur les compositeurs 
                if compositeur_list and compositeur_list!=[]:                
                    for i in range(len(compositeur_list)):
                        if compositeur_list[i]!='':
                            compo_api = get_api_externe(compositeur_list[i])
                            nom = compo_api.get("Nom")
                            prenom = compo_api.get("Prénom")
                            pays = compo_api.get("Pays")
                            IPI = compo_api.get("IPI")
                            ISNI = compo_api.get("ISNI")
                            compositeur = create_auteur(session, nom, prenom, pays, IPI, ISNI)
                            compositeur_id = compositeur.auteur_id
                            # partition.rel_auteur_partition.append(compositeur)
                            create_asso_auteur_partition(session, part_id, compositeur_id, 'compositeur')

                # Boucle sur les artistes 
                if artiste_list and artiste_list!=[]:                
                    for i in range(len(artiste_list)):
                        if artiste_list[i]!='':
                            artiste_api = get_api_externe(artiste_list[i])
                            nom = artiste_api.get("Nom")
                            prenom = artiste_api.get("Prénom")
                            pays = artiste_api.get("Pays")
                            IPI = artiste_api.get("IPI")
                            ISNI = artiste_api.get("ISNI")
                            artiste = create_auteur(session, nom, prenom, pays, IPI, ISNI)
                            artiste_id = artiste.auteur_id
                            create_asso_auteur_partition(session, part_id, artiste_id, 'artiste')

                # Boucle sur les arrangeurs 
                if arrangeur_list and arrangeur_list!=[]:                
                    for i in range(len(arrangeur_list)):
                        if arrangeur_list[i]!='':
                            arrangeur_api = get_api_externe(arrangeur_list[i])
                            nom = arrangeur_api.get("Nom")
                            prenom = arrangeur_api.get("Prénom")
                            pays = arrangeur_api.get("Pays")
                            IPI = arrangeur_api.get("IPI")
                            ISNI = arrangeur_api.get("ISNI")
                            arrangeur = create_auteur(session, nom, prenom, pays, IPI, ISNI)
                            arrangeur_id = arrangeur.auteur_id
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
    
# Insertion du csv users dans BDD
def insert_users_to_db(file_path):
    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        # Ouverture du fichier CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Parcours des lignes du fichier CSV
            for row in csv_reader:
                username = row.get('username')
                fullname = row.get('fullname')
                hashed_password = row.get('hashed_password')
                email = row.get('email')
                permissions = row.get('permissions')
                create_user_admin(session, username, fullname, hashed_password, email, permissions)    
 
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
user_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/sources/users.csv"
# event_path = "../sources/events.csv" # prompt au niveau E4/
# scrapy_path = "./harmonie/harmonie/nouveau.csv" # prompt au niveau E4/

# Importation des données CSV dans la base de données
insert_event_to_db(event_path)
insert_scrapy_to_db(scrapy_path)
insert_users_to_db(user_path)