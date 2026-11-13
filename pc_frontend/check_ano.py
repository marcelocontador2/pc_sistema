import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. O CAMPO DE ANO TEM ID 'ano'? ===")
# Procura o input do ano
match = re.search(r'<input[^>]*id="([^"]*ano[^"]*)"[^>]*>', s, re.IGNORECASE)
if match:
    print(f"  -> Encontrado: {match.group(0)}")
    print(f"  -> O ID do campo é: {match.group(1)}")
else:
    print("  -> NÃO encontrei um input com ID contendo 'ano'.")
    # Tenta achar qualquer input que pareça ser o ano
    inputs = re.findall(r'<input[^>]*>', s)
    for i in inputs:
        if '2026' in i or 'ano' in i.lower():
            print(f"  -> Possível input: {i}")

print("\n=== 2. COMO O JS PEGA O ANO? ===")
with open("dmpl_functions.js", "r", encoding="utf-8") as f:
    js = f.read()
    
# Mostra a linha do JS que pega o ano
for linha in js.split("\n"):
    if "getElementById" in linha and "ano" in linha.lower():
        print(f"  {linha.strip()}")
