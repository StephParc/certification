import csv
import pandas as pd
from datetime import date

# Récupération de la date du jour
date_du_jour = date.today()
date_str = date.today().strftime("%Y-%m-%d")

# Lecture des fichiers CSV
read_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/"
write_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/essais/"
input_file1 = "100-1600"
# input_file2 = "900-1600"
output_file = "musicshop_2025-02-27"
output_file = f"{write_path}{output_file}.csv"
# input_file1 = "musicshop_2025-02-27"
# input_file2 = "musicshop_last"
# output_file1 = f"{write_path}musicshop_{date_str}.csv"
# output_file2 = f"{read_path}{input_file2}.csv"
# output_file2 = f"{read_path}musicshop_last.csv"

path_csv1 = f"{read_path}{input_file1}.csv"
# path_csv2 = f"{read_path}{input_file2}.csv"

df1 = pd.read_csv(path_csv1, dtype={'ISMN': str, 'annee_sortie': str})
# df1 = pd.read_csv(path_csv1)
# df1['ISMN']= df1['ISMN'].astype(object)
# df1['annee_sortie'] = df1['annee_sortie'].astype(object)
# df2 = pd.read_csv(path_csv2, dtype={'ISMN': str, 'annee_sortie': str})
# df2 = pd.read_csv(path_csv2)
# df2['ISMN'] = df2['ISMN'].astype(object)
# df2['annee_sortie'] = df2['annee_sortie'].astype(object)
# Filtrer les lignes de df1 qui ne sont pas dans df2: nouveautés
# df_filtered = df1[~df1.apply(tuple, 1).isin(df2.apply(tuple, 1))].copy()
# df_combined = pd.concat([df1, df2], ignore_index=True)
# df_filtered["date_ajout"] = date_du_jour

# df_filtered.to_csv(output_file1, index=False)
df1["date_ajout"] = "2025-02-27"
df1.to_csv(output_file, index=False)
