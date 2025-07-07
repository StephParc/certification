import csv
import pandas as pd
from datetime import date

# Récupération de la date du jour
date_du_jour = date.today()
date_str = date.today().strftime("%Y-%m-%d")

# Lecture des fichiers CSV
read_path = ""
write_path = "archives/"

input_file1 = "musicshop_last"
input_file2 = "musicshop_all"

output_file1 = f"./{write_path}musicshop_{date_str}.csv"
output_file2 = f"./{read_path}musicshop_all.csv"
output_file3 = f"./{read_path}musicshop_new.csv"

path_csv1 = f"./{read_path}{input_file1}.csv"
path_csv2 = f"./{read_path}{input_file2}.csv"

df1 = pd.read_csv(path_csv1, dtype={'ISMN': str, 'annee_sortie': str})
df2 = pd.read_csv(path_csv2, dtype={'ISMN': str, 'annee_sortie': str})

# Filtrer les lignes de df1 qui ne sont pas dans df2: nouveautés
df_filtered = df1[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))].copy()

# Purger le fichier musicshop_new
with open(output_file3, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    header = next(reader)

with open(output_file3, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)

# Enregistrer les nouveautés
df_filtered.to_csv(output_file3, index=False)

# Complèter les nouveautés 
df_combined = pd.concat([df_filtered, df2], ignore_index=True)
df_combined.to_csv(output_file2, index=False)

# Archiver les nouveatés
df_filtered["date_ajout"] = date_du_jour
df_filtered.to_csv(output_file1, index=False)

