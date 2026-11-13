import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTAO VERIFICAR ===")
btn = re.search(r'<button[^>]*>([^<]*Verificar[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao 'Verificar' nao encontrado.")

print("\n=== 2. FUNCAO carregar() (existe?) ===")
match = re.search(r'function\s+carregar\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    print(bloco[:2500])
else:
    print("Funcao carregar() NAO ENCONTRADA no arquivo!")

print("\n=== 3. IDs DOS SELECTS DE FILTRO ===")
selects = re.findall(r'<select[^>]*id="([^"]+)"[^>]*>', s)
for sel in selects:
    print(f"  - {sel}")
