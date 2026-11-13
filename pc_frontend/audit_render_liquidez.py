import re

with open("liquidez.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== FUNÇÃO renderizarResultado ===")
match = re.search(r'function\s+renderizarResultado\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:3000])
else:
    print("Funcao nao encontrada.")
