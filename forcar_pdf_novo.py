import sys, os, json, asyncio, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.abspath("pc_backend"))
from main import api_relatorio_consolidado_novo, gerar_pdf_relatorio_consolidado

print("1. Gerando novo relatorio no banco...")
resultado = asyncio.run(api_relatorio_consolidado_novo("2026-TRIMESTRE-3"))

# Mostra na tela o que veio do JSON para o Comparativo de Receitas
for mod in resultado.get("encontrados", []):
    if mod.get("nome") == "Comparativo de Receitas":
        import psycopg2
        PG_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database", "user": "postgres", "password": "pc_admin_2026"}
        pg = psycopg2.connect(**PG_CONFIG)
        cur_pg = pg.cursor()
        cur_pg.execute("SELECT dados_json FROM historico_comparativo_receitas WHERE id = %s", (mod.get("id"),))
        r = cur_pg.fetchone()
        pg.close()
        if r:
            dados = json.loads(r[0])
            print("   Grupos retornados pela API:")
            for g in dados.get("atual", {}).get("grupos", []):
                print(f"   - {g.get('nome')}")

dados_consolidados = {
    "periodo": "2026-TRIMESTRE-3",
    "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "dados": resultado.get("encontrados", [])
}

conn = sqlite3.connect("pc_storage/banco_dados.db")
cur = conn.cursor()
cur.execute("INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
    ("2026-TRIMESTRE-3", dados_consolidados["data_geracao"], json.dumps(dados_consolidados, ensure_ascii=False)))
conn.commit()
novo_id = cur.lastrowid
conn.close()
print(f"\n2. Novo relatorio salvo no banco com ID {novo_id}")

print(f"\n3. Gerando PDF do relatorio {novo_id}...")
resposta = gerar_pdf_relatorio_consolidado(novo_id)
with open(f"relatorio_consolidado_{novo_id}.pdf", "wb") as f:
    f.write(resposta.body)
print(f"✅ PDF gerado: relatorio_consolidado_{novo_id}.pdf")
