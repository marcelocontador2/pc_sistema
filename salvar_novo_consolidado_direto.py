import sys, os, json, asyncio, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.abspath("pc_backend"))

from main import api_relatorio_consolidado_novo

# Chama a API (que agora inclui o DMPL)
resultado = asyncio.run(api_relatorio_consolidado_novo("2026-TRIMESTRE-3"))

if resultado.get("status") != "ok":
    print("❌ Erro na API:", resultado)
    sys.exit(1)

dados_consolidados = {
    "periodo": "2026-TRIMESTRE-3",
    "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "dados": resultado.get("encontrados", [])
}

# Salva no SQLite
conn = sqlite3.connect("pc_storage/banco_dados.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        periodo TEXT,
        data_geracao TEXT,
        resultado_json TEXT
    )
""")
cur.execute(
    "INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
    ("2026-TRIMESTRE-3", dados_consolidados["data_geracao"], json.dumps(dados_consolidados, ensure_ascii=False))
)
conn.commit()
novo_id = cur.lastrowid
conn.close()

print(f"✅ Novo relatório salvo no SQLite com ID {novo_id}")
print(f"   Módulos incluídos: {len(dados_consolidados['dados'])}")
for m in dados_consolidados["dados"]:
    print(f"   - {m.get('nome')} (id={m.get('id')})")
