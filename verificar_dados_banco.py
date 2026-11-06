import sqlite3, json, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# BF
print("=" * 70)
print("DADOS DO BF NO BANCO")
print("=" * 70)
cursor.execute("SELECT id, periodo FROM historico_analise_financeira_bf ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"Período no banco: '{row[1]}'")
    print(f"Bytes do período: {row[1].encode('utf-8')}")

# DFC
print("\n" + "=" * 70)
print("DADOS DO DFC NO BANCO")
print("=" * 70)
cursor.execute("SELECT id, periodo, resultado_json FROM historico_analise_dfc ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"Período no banco: '{row[1]}'")
    print(f"Bytes do período: {row[1].encode('utf-8')}")
    
    # Verifica se o JSON tem acentos
    dados = json.loads(row[2])
    json_str = json.dumps(dados, ensure_ascii=False)
    print(f"\nJSON (primeiros 500 chars):")
    print(json_str[:500])
    print(f"\nTem acento no JSON? {'Sim' if any(ord(c) > 127 for c in json_str) else 'Não'}")

conn.close()
