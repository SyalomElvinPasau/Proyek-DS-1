import pandas as pd
import glob
import os

file_paths = glob.glob("C:/Users/azrie/OneDrive/UNPAR/Materi Pembelajaran Informatika/Semester 6/Proyek Data Science 1/Tugas/Kode/Proyek-DS-1/Result Restaurant/csv/*.csv")  # Ganti folder_path dengan lokasi folder

df_list = []

for file in file_paths:
    kelurahan_name = os.path.basename(file).replace(".csv", "")

    df = pd.read_csv(file, encoding="ISO-8859-1") 
    df["Kelurahan"] = kelurahan_name 

    df_list.append(df)  

df_combined = pd.concat(df_list, ignore_index=True)

df_combined.to_csv("combinedCSVRestaurant.csv", index=False)
