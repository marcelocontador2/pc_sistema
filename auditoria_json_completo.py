import sqlite3, json, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

modulos = {
    "integridade": "historico_integridade_matriz",
    "analise_bp": "historico_analise_bp",
    "analise_orcamentaria": "historico_analise_orcamentaria",
    "analise_financeira_bf": "historico_analise_financeira_bf",
    "analise_dfc": "historico_analise_dfc",
    "analise_patrimonial": "historico_analise_patrimonial",
    "comparativo_receitas": "historico_comparativo_receitas",
    "comparativo_despesas": "historico_comparativo_despesas",
    "liquidez": "historico_liquidez",
    "panorama": "historico_panorama",
    "centro_custos": "historico_centro_custos",
    "custo_pessoal": "historico_custo_pessoal",
}

periodo = "2026-TRIMESTRE-3"

for chave, tabela in modulos.items():
    col = "dados_json" if "comparativo" in tabela or "centro" in tabela else "resultado_json"
    try:
        cursor.execute(f"SELECT {col} FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
        row = cursor.fetchone()
        if row:
            d = json.loads(row[0])
            print(f"\n{'='*70}")
            print(f"MÓDULO: {chave} (tabela: {tabela})")
            print(f"{'='*70}")
            print(json.dumps(d, indent=2, ensure_ascii=False)[:1500])
            print("... (truncado)" if len(json.dumps(d)) > 1500 else "")
        else:
            print(f"\n[VAZIO] {chave} (sem histórico para {periodo})")
    except Exception as e:
        print(f"\n[ERRO] {chave}: {e}")

conn.close()
