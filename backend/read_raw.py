import json

log_path = r"C:\Users\User\.gemini\antigravity-ide\brain\60ee8762-b276-4941-8422-d79730d59409\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    line = f.readline()
    data = json.loads(line)
    content = data.get('content', '')
    
    if "truncated" in content:
        print("La palabra 'truncated' está en el contenido del log físico.")
        # Imprimir parte de alrededor de 'truncated'
        idx = content.find("truncated")
        print("Contexto:", content[max(0, idx-50):min(len(content), idx+50)])
    else:
        print("No se encontró 'truncated' físicamente. ¡Los datos están completos!")
        print("Longitud total del contenido:", len(content))
        with open("completo.txt", "w", encoding="utf-8") as out:
            out.write(content)
