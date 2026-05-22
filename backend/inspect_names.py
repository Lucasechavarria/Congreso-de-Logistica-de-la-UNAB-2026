import pandas as pd
import sys

excel_path = "../Congreso_de_Logística_2026.xlsx"
try:
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
    for idx, row in df.iterrows():
        print(f"{idx}: Nombre='{row['Nombre']}', Apellido='{row['apellido']}'")
except Exception as e:
    print("Error:", e)
