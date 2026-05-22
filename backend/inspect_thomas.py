import pandas as pd
excel_path = "../Congreso_de_Logística_2026.xlsx"
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip()
row_6 = df.iloc[6]
print("Nombre:", row_6['Nombre'])
print("Apellido:", row_6['apellido'])
print("Email:", row_6['EMAIL'])
print("DNI:", row_6['DNI'])
