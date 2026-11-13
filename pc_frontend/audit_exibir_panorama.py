import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNCAO exibirSelecionado() ===")
match = re.search(r'async function\s+exibirSelecionado\(\)\s*\{.*?\n\}', s, re.DOTALL)
if match:
    print(match.group(0)[:1500])
else:
    print("Funcao nao encontrada.")

print("\n=== 2. CLASSE DO CHECKBOX NO HISTÓRICO ===")
# Procura o checkbox que o JS usa
if "check-hist" in s:
    print("SIM, a classe 'check-hist' existe no HTML.")
else:
    print("NAO, a classe 'check-hist' NAO existe no HTML.")
    
if "check-historico" in s:
    print("SIM, a classe 'check-historico' existe no HTML.")
else:
    print("NAO, a classe 'check-historico' NAO existe no HTML.")

print("\n=== 3. ELEMENTO #lista-historico ===")
if 'id="lista-historico"' in s:
    print("SIM, o ID 'lista-historico' existe no HTML.")
else:
    print("NAO, o ID 'lista-historico' NAO existe no HTML.")
