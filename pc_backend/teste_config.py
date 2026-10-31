import httpx
import json

print("=== GET /api/configuracoes ===")
r = httpx.get("http://127.0.0.1:9999/api/configuracoes")
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

print("\n=== POST /api/configuracoes (mudar para COREN) ===")
r = httpx.post("http://127.0.0.1:9999/api/configuracoes", json={"tipo_entidade": "COREN"})
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

print("\n=== GET /api/configuracoes (verificar) ===")
r = httpx.get("http://127.0.0.1:9999/api/configuracoes")
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
