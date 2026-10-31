import httpx
r = httpx.get("http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3?entidade=COREN")
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type')}")
print(f"Body (primeiros 2000 chars):")
print(r.text[:2000])
