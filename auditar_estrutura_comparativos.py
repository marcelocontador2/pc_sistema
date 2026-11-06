import sqlite3, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for tab in ["historico_comparativo_receitas", "historico_comparativo_despesas"]:
    print(f"\n=== ESTRUTURA DA TABELA {tab} ===")
    try:
        cursor.execute(f"PRAGMA table_info({tab})")
        colunas = cursor.fetchall()
        for col in colunas:
            print(f"  Coluna: {col[1]} | Tipo: {col[2]}")
        
        print(f"\n  Últimos registros:")
        cursor.execute(f"SELECT * FROM {tab} ORDER BY id DESC LIMIT 2")
        rows = cursor.fetchall()
        for r in rows:
            print(f"  {r}")
    except Exception as e:
        print(f"  ERRO: {e}")

conn.close()
