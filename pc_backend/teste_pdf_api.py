import httpx
import json

# Teste com entidade=COREN na URL
r = httpx.get("http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3?entidade=COREN")
d = r.json()
print(f"Status: {r.status_code}")
print(f"limite_pct: {d.get('limite_pct')}")
print(f"limite_atual: {d.get('limite_atual')}")
print(f"margem: {d.get('margem_disponivel_atual')}")
