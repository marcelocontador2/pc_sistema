import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. ESTRUTURA DE UM CARD NO HTML ===")
# Pega o primeiro bloco de card completo
match = re.search(r'(<div class="card">.*?</div>)', s, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("Card nao encontrado.")

print("\n=== 2. FUNCAO preencherCards() ATUAL ===")
match = re.search(r'function\s+preencherCards\([^)]*\)\s*\{.*?\n\}', s, re.DOTALL)
if match:
    print(match.group(0)[:1500])
else:
    print("Funcao nao encontrada.")
