import csv
import pandas as pd
from datetime import date

# Récupération de la date du jour
date_du_jour = date.today()
date_str = date.today().strftime("%Y-%m-%d")

# Lecture des fichiers CSV
read_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/"
write_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/essais/"
input_file1 = "musicshop_new"
input_file2 = "musicshop_last"
# input_file1 = "nouveau"
# input_file2 = "musicshop_last"
output_file1 = f"{write_path}musicshop_{date_str}.csv"
# output_file2 = f"{read_path}{input_file2}.csv"
output_file2 = f"{read_path}musicshop_last.csv"

path_csv1 = f"{read_path}{input_file1}.csv"
path_csv2 = f"{read_path}{input_file2}.csv"

df1 = pd.read_csv(path_csv1, dtype={'ISMN': str, 'annee_sortie': str})
df2 = pd.read_csv(path_csv2, dtype={'ISMN': str, 'annee_sortie': str})

# Filtrer les lignes de df1 qui ne sont pas dans df2: nouveautés
df_filtered = df1[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))].copy()
df_combined = pd.concat([df_filtered, df2], ignore_index=True)
df_filtered["date_ajout"] = date_du_jour

df_filtered.to_csv(output_file1, index=False)
df_combined.to_csv(output_file2, index=False)
