import sqlite3, json, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Verifica o que está no histórico consolidado id=8
cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = 8")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]} | Período: {row[1]} | Data: {row[2]}")
    dados = json.loads(row[3])
    print(f"Chaves do JSON: {list(dados.keys())}")
    print(f"Chaves dentro de 'dados': {list(dados.get('dados', {}).keys())}")
    
    # Verifica se algum módulo tem dados
    for chave, valor in dados.get('dados', {}).items():
        if isinstance(valor, dict):
            tem_dados = 'dados' in valor or any(k in valor for k in ['ativo_total', 'liquidez', 'matriz', 'centros', 'rcl_total'])
            print(f"  {chave}: {'TEM dados' if tem_dados else 'VAZIO'}")
else:
    print("Histórico id=8 não encontrado.")

# 2. Lista todos os históricos consolidados existentes
print("\n" + "=" * 70)
print("TODOS OS HISTÓRICOS CONSOLIDADOS")
print("=" * 70)
cursor.execute("SELECT id, periodo, data_geracao FROM historico_relatorio_consolidado ORDER BY id DESC")
for r in cursor.fetchall():
    print(f"  ID: {r[0]} | Período: {r[1]} | Data: {r[2]}")

conn.close()
