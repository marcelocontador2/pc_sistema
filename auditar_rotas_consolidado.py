import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

print("=== 1. TODAS AS DEFINIÇÕES DE api_relatorio_consolidado ===")
for m in re.finditer(r'async def (api_relatorio_consolidado\w*)\s*\(', codigo):
    print(f"  -> {m.group(1)} (posição {m.start()})")

print("\n=== 2. ROTAS QUE CHAMAM ALGUMA api_relatorio_consolidado ===")
for m in re.finditer(r'@app\.(get|post)\("(/api/relatorio_consolidado[^"]*)"\).*?async def (\w+).*?\n(.*?)(?=\n@app\.|\Z)', codigo, re.DOTALL):
    rota = m.group(2)
    func = m.group(3)
    corpo = m.group(4)[:300]
    print(f"  Rota: {rota} -> Função: {func}")
    print(f"  Corpo: {corpo.strip()[:150]}...\n")
