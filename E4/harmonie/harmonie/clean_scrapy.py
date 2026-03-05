# clean_scrapy.py
import pandas as pd
from datetime import date
from utils.S3_utils import read_csv_from_datalake, upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - Nettoyage scrapy"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def clean_scrapy_S3():
    # Récupération de la date du jour
    date_du_jour = date.today()
    date_str = date.today().strftime("%Y-%m-%d")

    # Types à forcer pour éviter les .0 sur id et int
    DTYPE_CONFIG = {'ISMN': str, 'annee_sortie': str}

    # Lecture des fichiers depuis S3
    df_last = read_csv_from_datalake("zone-brutes", "E4/musicshop_last.csv", dtype=DTYPE_CONFIG)
    if df_last is None:
        logger.critical("Impossible de lire le fichier source")
        return False
    
    df_all = read_csv_from_datalake("zone-propres", "E4/musicshop_all.csv", dtype=DTYPE_CONFIG)
    if df_all is None:
        logger.info("Fichier musicshop_all introuvable, initialisation d'un nouvel historique")
        df_all =pd.DataFrame(columns=df_last.columns)

    # Filtrer les lignes de df_last qui ne sont pas dans df_all: nouveautés
    df_new = df_last[~df_last.apply(tuple, 1).isin(df_all.apply(tuple, 1))].copy()

    if not df_new.empty:
        # Chemins temporaires pour l'upload
        tmp_new = "/tmp/musicshop_new.csv"
        tmp_all = "/tmp/musicshop_all.csv"
        tmp_archive = "/tmp/musicshop_archive.csv"
        tmp_old_all = "/tmp/musicshop_old_all.csv"

        # Sécuriser musicshop_all
        df_all.to_csv(tmp_old_all, index=False)
        upload_file(
            local_path=tmp_old_all, 
            bucket="zone-propres", 
            s3_path="E4/archives/musicshop_all.csv",
            metadata={
                "source": "Scraping musicshopeurope",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/archives/"
            })

        # Enregistrer les nouveautés
        df_new.to_csv(tmp_new, index=False)
        upload_file(
            local_path=tmp_new, 
            bucket="zone-propres", 
            s3_path="E4/musicshop_new.csv",
            metadata={
                "source": "zone-brutes/E4/musicshop_last.csv et zone-propres/E4/musicshop_all.csv",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "hbm.public.TB_[auteur, partition]"
            })

        # Compléter les données avec les nouveautés 
        df_combined = pd.concat([df_new, df_all], ignore_index=True)
        df_combined.to_csv(tmp_all, index=False)     
        upload_file(
            local_path=tmp_all, 
            bucket="zone-propres", 
            s3_path="E4/musicshop_all.csv",
            metadata={
                "source": "Scraping musicshopeurope",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/"
            })

        # Archiver les nouveautés
        df_new["date_ajout"] = date_du_jour
        df_new.to_csv(tmp_archive, index=False)
        upload_file(
            local_path=tmp_archive, 
            bucket="zone-propres", 
            s3_path=f"E4/archives/musicshop_{date_str}.csv",
            metadata={
                "source": "zone-propres/E4/musicshop_new.csv",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/archives/"
            })

        logger.info(f"{len(df_new)} nouveautés traitées.")
        return True
    
    logger.info("Aucune nouveauté détectée.")
    return False

if __name__ == "__main__":
    clean_scrapy_S3()

# # ********** Version locale en exécution procédurale directe **********
# # Récupération de la date du jour
# date_du_jour = date.today()
# date_str = date.today().strftime("%Y-%m-%d")

# # Lecture des fichiers CSV
# read_path = ""
# write_path = "archives/"

# input_file1 = "musicshop_last"
# input_file2 = "musicshop_all"

# output_file1 = f"./{write_path}musicshop_{date_str}.csv"
# output_file2 = f"./{read_path}musicshop_all.csv"
# output_file3 = f"./{read_path}musicshop_new.csv"

# path_csv1 = f"./{read_path}{input_file1}.csv"
# path_csv2 = f"./{read_path}{input_file2}.csv"

# df1 = pd.read_csv(path_csv1, dtype={'ISMN': str, 'annee_sortie': str}) # musicshop_last
# df2 = pd.read_csv(path_csv2, dtype={'ISMN': str, 'annee_sortie': str}) # musicshop_all

# # Filtrer les lignes de df1 qui ne sont pas dans df2: nouveautés
# df_filtered = df1[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))].copy()

# # Purger le fichier musicshop_new
# with open(output_file3, mode='r', newline='', encoding='utf-8') as infile:
#     reader = csv.reader(infile)
#     header = next(reader)

# with open(output_file3, mode='w', newline='', encoding='utf-8') as outfile:
#     writer = csv.writer(outfile)
#     writer.writerow(header)

# # Enregistrer les nouveautés
# df_filtered.to_csv(output_file3, index=False) # musicshop_new

# # Compléter les nouveautés 
# df_combined = pd.concat([df_filtered, df2], ignore_index=True)
# df_combined.to_csv(output_file2, index=False) # musicshop_all

# # Archiver les nouveatés 
# df_filtered["date_ajout"] = date_du_jour
# df_filtered.to_csv(output_file1, index=False) # musicshop_{date_du_jour} archive

