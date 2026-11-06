import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

print("=== 1. TABELAS DE HISTÓRICO ENCONTRADAS ===")
tabelas = sorted(set(re.findall(r'CREATE TABLE IF NOT EXISTS (\w*historico\w*)', codigo, re.IGNORECASE)))
for t in tabelas:
    print(f" - {t}")

print("\n=== 2. FUNÇÕES DE CÁLCULO (api_*) ===")
funcs = sorted(set(re.findall(r'async def (api_\w+)\s*\(', codigo)))
for fn in funcs:
    print(f" - {fn}")

print("\n=== 3. ROTAS DE SALVAR ===")
rotas = sorted(set(re.findall(r'@app\.(?:get|post)\("(/salvar_\w+)', codigo)))
for r in rotas:
    print(f" - {r}")
