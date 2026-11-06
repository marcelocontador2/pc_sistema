import sqlite3, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tabelas = [
    "historico_analise_financeira_bf",
    "historico_comparativo_receitas",
    "historico_comparativo_despesas"
]

for tab in tabelas:
    print(f"\n=== {tab} ===")
    try:
        cursor.execute(f"SELECT id, periodo, length(periodo), hex(periodo) FROM {tab} ORDER BY id DESC LIMIT 3")
        for r in cursor.fetchall():
            print(f"ID: {r[0]} | Período: '{r[1]}' | Tamanho: {r[2]} | Hex: {r[3]}")
    except Exception as e:
        print("Erro:", e)

conn.close()
