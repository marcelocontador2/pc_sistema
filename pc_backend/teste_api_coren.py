import httpx
import json

url = "http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3?entidade=COREN"
r = httpx.get(url)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:2000])
