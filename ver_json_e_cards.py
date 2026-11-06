import requests, json, sqlite3, os, re

print("=== 1) O QUE ESTÁ SALVO NO BANCO (ID MAIS RECENTE) ===")
db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, periodo, resultado_json FROM historico_panorama ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
conn.close()

if row:
    print(f"ID: {row[0]} | Periodo: {row[1]}")
    d = json.loads(row[2])
    print(json.dumps(d, indent=2, ensure_ascii=False))
else:
    print("Banco vazio.")

print("\n=== 2) TRECHO DO HTML ONDE ESTÃO OS CARDS ===")
with open("pc_frontend/panorama.html", "r", encoding="utf-8") as f:
    html = f.read()

# Acha onde começa a div principal que contém os cards
idx = html.find('Resultados Gerais')
if idx != -1:
    print(html[idx-100:idx+1500])
else:
    print("Nao achei 'Resultados Gerais' no HTML.")
