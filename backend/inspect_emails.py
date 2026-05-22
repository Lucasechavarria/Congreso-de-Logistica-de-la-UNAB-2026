import pandas as pd

excel_path = "../Congreso_de_Logística_2026.xlsx"
try:
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
    
    def limpiar_email(email):
        if not isinstance(email, str):
            return ""
        email = email.strip().lower()
        email = email.replace("..com", ".com")
        email = email.replace(",", ".")
        if email.endswith("@gmail"):
            email = email + ".com"
        return email

    for idx, row in df.iterrows():
        orig = str(row['EMAIL']).strip()
        limpio = limpiar_email(orig)
        if orig != limpio or ".." in orig or "," in orig or not orig.endswith(".com"):
            print(f"{idx}: Original='{orig}', Limpio='{limpio}'")
except Exception as e:
    print("Error:", e)
