import pandas as pd
import sys

excel_path = "../Congreso_de_Logística_2026.xlsx"
try:
    df = pd.read_excel(excel_path)
    print("Columnas encontradas en el Excel:")
    print(df.columns.tolist())
    print("\nPrimeras 5 filas:")
    print(df.head())
    print("\nCantidad total de registros:", len(df))
except Exception as e:
    print("Error al leer el excel:", e)
    sys.exit(1)
