import csv
import pandas as pd
from datetime import date

# Récupération de la date du jour
date_du_jour = date.today()
date_str = date.today().strftime("%Y-%m-%d")

# Lecture des fichiers CSV
read_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/"
write_path = "C:/Users/Stephanie/Documents/Formations_info/Simplon/Certification/E4/harmonie/harmonie/"
input_file1 = "musicshop0100"
input_file2 = "musicshop0200"
output_file = "100-200"
output_file = f"{write_path}{output_file}.csv"


path_csv1 = f"{read_path}{input_file1}.csv"
path_csv2 = f"{read_path}{input_file2}.csv"

df1 = pd.read_csv(path_csv1, dtype={'ISMN': str, 'annee_sortie': str}, encoding='UTF-8')
df2 = pd.read_csv(path_csv2, dtype={'ISMN': str, 'annee_sortie': str}, encoding='UTF-8')

df_combined = pd.concat([df1, df2], ignore_index=True)

df_combined.to_csv(output_file, index=False)
