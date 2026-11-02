import sqlite3, os, json

db_path = os.path.join(os.getcwd(), "..", "pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, periodo, data_geracao FROM historico_centro_custos ORDER BY id DESC")
rows = cur.fetchall()

print("=== HISTÓRICOS DE CENTRO DE CUSTOS NO BANCO ===")
if not rows:
    print("Nenhum registro encontrado.")
else:
    for r in rows:
        print(f"ID: {r[0]} | Período: {r[1]} | Data: {r[2]}")

conn.close()
