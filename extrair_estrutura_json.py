import psycopg2
import json

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

print("="*70)
print("🔍 EXTRAINDO ESTRUTURA DOS JSONs PARA 2026-TRIMESTRE-3")
print("="*70)

tabelas = [
    ("historico_integridade_matriz", "resultado_json"),
    ("historico_analise_bp", "resultado_json"),
    ("historico_analise_orcamentaria", "resultado_json"),
    ("historico_analise_financeira_bf", "resultado_json"),
    ("historico_analise_dfc", "resultado_json"),
    ("historico_analise_patrimonial", "resultado_json"),
    ("historico_analise_dmpl", "resultado_json"),
    ("historico_comparativo_receitas", "dados_json"),
    ("historico_comparativo_despesas", "dados_json"),
    ("historico_liquidez", "resultado_json"),
    ("historico_panorama", "resultado_json"),
    ("historico_centro_custos", "dados_json"),
    ("historico_custo_pessoal", "resultado_json"),
    ("historico_conferencia", "resultado_json")
]

conn = psycopg2.connect(**PG_CONFIG)
cursor = conn.cursor()

for tabela, coluna in tabelas:
    try:
        cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE periodo LIKE '%2026-TRIMESTRE-3%' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0]:
            dados = json.loads(row[0])
            print(f"\n{'='*70}")
            print(f"📊 {tabela}")
            print(f"{'='*70}")
            print(json.dumps(dados, ensure_ascii=False, indent=2)[:1500])
        else:
            print(f"\n❌ {tabela}: sem dados")
    except Exception as e:
        print(f"\n❌ {tabela}: erro - {e}")

cursor.close()
conn.close()
