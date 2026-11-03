import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("BUSCANDO ROTAS DE ANÁLISE FINANCEIRA NO MAIN.PY")
print("=" * 70)

# Busca qualquer rota que tenha "financeira" no nome
matches = re.finditer(r'(@app\.(?:get|post|put|delete)\([^)]*financeira[^)]*\)\s*\n(?:async\s+)?def\s+([a-zA-Z0-9_]+)\([^)]*\))', c, re.IGNORECASE)

encontrou = False
for m in matches:
    print("\n" + "-"*40)
    print(m.group(1))
    encontrou = True

if not encontrou:
    print("\n[AVISO] Nenhuma rota de 'financeira' encontrada no main.py.")
