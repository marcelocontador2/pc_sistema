import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. EVENT LISTENER OU ONCLICK DO BOTAO ===")
# Procura por btn-exibir-composicao no JS
match = re.search(r'btn-exibir-composicao.*?addEventListener.*?\);', s, re.DOTALL)
if match:
    print("Event listener encontrado:")
    print(match.group(0))
else:
    print("Nenhum event listener direto encontrado para 'btn-exibir-composicao'.")
    
    # Procura onclick
    if 'onclick="exibirSelecionado()"' in s:
        print("O HTML TEM onclick direto.")
    else:
        print("O HTML NAO tem onclick direto. O botao pode estar orfao!")

print("\n=== 2. FUNCAO renderTabela (existe?) ===")
if 'function renderTabela' in s:
    print("SIM, a funcao renderTabela existe no arquivo.")
else:
    print("NAO, a funcao renderTabela NAO existe.")

print("\n=== 3. FUNCAO renderChart (existe?) ===")
if 'function renderChart' in s:
    print("SIM, a funcao renderChart existe no arquivo.")
else:
    print("NAO, a funcao renderChart NAO existe.")
