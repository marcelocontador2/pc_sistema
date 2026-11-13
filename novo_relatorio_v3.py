import sys, os, json, asyncio, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.abspath("pc_backend"))
from main import api_relatorio_consolidado_novo
resultado = asyncio.run(api_relatorio_consolidado_novo("2026-TRIMESTRE-3"))
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
print(f"✅ Novo relatório salvo com ID {novo_id}")
