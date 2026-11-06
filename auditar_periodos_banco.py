import sqlite3, os, json

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 1. PERÍODOS NA TABELA historico_comparativo_receitas ===")
try:
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_receitas ORDER BY id DESC LIMIT 5")
    for r in cursor.fetchall():
        print(f"ID: {r[0]} | Período: '{r[1]}' | Data: {r[2]}")
except Exception as e:
    print("Erro:", e)

print("\n=== 2. PERÍODOS NA TABELA historico_comparativo_despesas ===")
try:
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_despesas ORDER BY id DESC LIMIT 5")
    for r in cursor.fetchall():
        print(f"ID: {r[0]} | Período: '{r[1]}' | Data: {r[2]}")
except Exception as e:
    print("Erro:", e)

print("\n=== 3. PERÍODOS NA TABELA historico_panorama (para comparar) ===")
try:
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_panorama ORDER BY id DESC LIMIT 5")
    for r in cursor.fetchall():
        print(f"ID: {r[0]} | Período: '{r[1]}' | Data: {r[2]}")
except Exception as e:
    print("Erro:", e)

conn.close()
