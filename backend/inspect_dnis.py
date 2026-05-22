import pandas as pd
import re

excel_path = "../Congreso_de_Logística_2026.xlsx"
try:
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
    
    for idx, row in df.iterrows():
        orig = str(row['DNI']).strip()
        # Limpiar
        dni_limpio = re.sub(r'\D', '', orig)
        if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
            dni_limpio = dni_limpio[0:8]
        
        if len(dni_limpio) != 8:
            print(f"{idx}: DNI original='{orig}', Limpio='{dni_limpio}', Largo={len(dni_limpio)}")
except Exception as e:
    print("Error:", e)
