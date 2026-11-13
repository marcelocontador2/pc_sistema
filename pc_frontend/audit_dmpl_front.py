import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNÇÃO exibirSelecionado (OU SIMILAR) NO DMPL ===")
# Procura a função que exibe os dados (pode ter nomes como exibirSelecionado, exibirHistorico, etc)
funcoes = re.findall(r'function\s+(\w*exibir\w*|\w*carregarHistorico\w*)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if not funcoes:
    print("Nenhuma função com 'exibir' ou 'carregarHistorico' encontrada.")
else:
    for f in funcoes:
        print(f"\n--- Função encontrada ---")
        print(f[:2000]) # Mostra até 2000 caracteres
        
print("\n=== 2. ROTAS FETCH NO DMPL ===")
# Procura todos os fetch no arquivo
fetches = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]\)', s)
for f in sorted(set(fetches)):
    print(f"  - {f}")
