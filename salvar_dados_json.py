import urllib.request
import json

# 1. Busca os dados da API
url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
with urllib.request.urlopen(url, timeout=10) as r:
    data = json.loads(r.read().decode())

# 2. Salva os dados em um arquivo JSON para o navegador ler
with open("pc_frontend/dados_despesas.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Dados salvos em pc_frontend/dados_despesas.json")
print(f"   Grupos: {len(data['atual']['grupos'])}")
print(f"   Empenhado: {data['atual']['empenhado_total']}")
