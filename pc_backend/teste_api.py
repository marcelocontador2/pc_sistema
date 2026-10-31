import httpx
r = httpx.get("http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3")
print(f"Status: {r.status_code}")
print(r.json())
