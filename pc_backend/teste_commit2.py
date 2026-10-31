import httpx
import json

print("=== 1. Verificar config atual ===")
r = httpx.get("http://127.0.0.1:9999/api/configuracoes")
print(f"Status: {r.status_code} | {r.json()}")

print("\n=== 2. Chamar /api/custo_pessoal SEM entidade (deve usar COFEN) ===")
r = httpx.get("http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3")
d = r.json()
print(f"Status: {r.status_code}")
print(f"  limite_pct: {d.get('limite_pct')}")
print(f"  limite_atual: {d.get('limite_atual')}")
print(f"  margem_disponivel_atual: {d.get('margem_disponivel_atual')}")
print(f"  entidade: {d.get('entidade')}")

print("\n=== 3. Mudar config para COREN ===")
r = httpx.post("http://127.0.0.1:9999/api/configuracoes", json={"tipo_entidade": "COREN"})
print(f"Status: {r.status_code} | {r.json()}")

print("\n=== 4. Chamar /api/custo_pessoal SEM entidade (deve usar COREN) ===")
r = httpx.get("http://127.0.0.1:9999/api/custo_pessoal/2026-TRIMESTRE-3")
d = r.json()
print(f"Status: {r.status_code}")
print(f"  limite_pct: {d.get('limite_pct')}")
print(f"  limite_atual: {d.get('limite_atual')}")
print(f"  margem_disponivel_atual: {d.get('margem_disponivel_atual')}")
print(f"  entidade: {d.get('entidade')}")

print("\n=== 5. Restaurar para COFEN ===")
r = httpx.post("http://127.0.0.1:9999/api/configuracoes", json={"tipo_entidade": "COFEN"})
print(f"Status: {r.status_code} | {r.json()}")
