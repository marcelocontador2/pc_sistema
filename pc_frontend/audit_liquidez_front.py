import re

with open("liquidez.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNÇÃO exibirSelecionado (OU SIMILAR) ===")
match = re.search(r'function\s+(exibirSelecionado|exibir|carregarHistoricoSelecionado)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:2000])
else:
    print("Funcao nao encontrada.")

print("\n=== 2. FUNÇÃO verificarIndices (OU SIMILAR) ===")
match = re.search(r'function\s+(verificarIndices|verificar|carregar)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:2000])
else:
    print("Funcao nao encontrada.")
