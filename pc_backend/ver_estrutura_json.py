import sqlite3, os, json

db_path = os.path.join(os.getcwd(), "..", "pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = '2026-TRIMESTRE-3' ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
conn.close()

if row:
    dados = json.loads(row[0])
    print("Chaves do JSON:", list(dados.keys()))
    print("\nPrimeiro centro:", dados.get("centros", [{}])[0] if dados.get("centros") else "Nenhum")
else:
    print("Nenhum dado encontrado.")
