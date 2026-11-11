import psycopg2
import json

PG = dict(host='localhost', port=5433, database='pc_database', user='postgres', password='pc_admin_2026')
conn = psycopg2.connect(**PG)
cur = conn.cursor()

tabelas = [
    ('historico_analise_bp', 'Balanço Patrimonial'),
    ('historico_analise_dfc', 'DFC'),
    ('historico_analise_dmpl', 'DMPL'),
    ('historico_analise_financeira_bf', 'Balanço Financeiro'),
    ('historico_analise_orcamentaria', 'Balanço Orçamentário')
]

for tab, nome in tabelas:
    try:
        cur.execute(f"SELECT resultado_json FROM {tab} WHERE periodo = %s ORDER BY id DESC LIMIT 1", ('2026-TRIMESTRE-3',))
        row = cur.fetchone()
        if row:
            dados = json.loads(row[0])
            print(f"\n=== {nome} ({tab}) ===")
            print("Chaves:", list(dados.keys())[:10])
            print("Resumo:", str(dados)[:300].replace('\n', ' '), "...")
        else:
            print(f"\n=== {nome} ({tab}) === Nao encontrado para o T3")
    except Exception as e:
        print(f"\nErro na tabela {tab}: {e}")

conn.close()
