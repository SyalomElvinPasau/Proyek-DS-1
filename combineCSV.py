import pandas as pd
import glob
import os

file_paths = glob.glob("/home/elvin/Documents/Code/College/Proyek Data Science/Proyek-DS-1/Result Hospital/csv/*.csv")  # Ganti folder_path dengan lokasi folder

df_list = []

for file in file_paths:
    kelurahan_name = os.path.basename(file).replace(".csv", "")

    df = pd.read_csv(file, encoding="ISO-8859-1") 
    df["Kelurahan"] = kelurahan_name 

    df_list.append(df)  

df_combined = pd.concat(df_list, ignore_index=True)

df_combined.to_csv("combinedCSV.csv", index=False)
