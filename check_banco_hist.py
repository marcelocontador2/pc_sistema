import sqlite3, json

db_path = "pc_storage/banco_dados.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, periodo, data_geracao FROM historico_integridade_matriz ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()

print("Ultimos 5 registros em historico_integridade_matriz:")
if not rows:
    print("  (Nenhum registro encontrado)")
for r in rows:
    print(f"  ID: {r[0]} | Periodo: {r[1]} | Data: {r[2]}")

conn.close()
