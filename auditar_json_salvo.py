import sqlite3, os, json

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== ÚLTIMOS 3 REGISTROS NO HISTÓRICO CONSOLIDADO ===")
cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC LIMIT 3")
rows = cursor.fetchall()

for r in rows:
    print(f"\nID: {r[0]}")
    print(f"Período: {r[1]}")
    print(f"Data: {r[2]}")
    print(f"JSON (primeiros 500 chars):")
    print(str(r[3])[:500] + "...")
    
    # Tenta ver a estrutura
    try:
        d = json.loads(r[3])
        print(f"\nChaves do JSON: {list(d.keys())}")
        if 'dados' in d:
            print(f"Chaves dentro de 'dados': {list(d['dados'].keys())}")
            print(f"Tipo de 'dados': {type(d['dados'])}")
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")

conn.close()
