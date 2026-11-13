import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. IDS DOS CARDS NO HTML ===")
# Procura todos os elementos que parecem ser os cards (divs com classes ou ids)
cards = re.findall(r'<div[^>]*class="[^"]*card[^"]*"[^>]*>', s)
if cards:
    for c in cards:
        print(f"  {c}")
else:
    print("  Nenhum card com a classe 'card' encontrado.")
    
# Procura por elementos que tenham 'card-' no ID
ids = re.findall(r'id="([^"]*card[^"]*)"', s)
if ids:
    print("\n  IDs que contém 'card':")
    for i in ids:
        print(f"    - {i}")

print("\n=== 2. FUNCAO preencherCards() NO JS ===")
match = re.search(r'function\s+preencherCards\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:1500])
else:
    print("Funcao preencherCards nao encontrada.")
