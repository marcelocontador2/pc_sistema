with open(r"pc_frontend\analise_comparativo_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mostra o trecho da função carregarHistorico
print("=== FUNÇÃO carregarHistorico ===")
idx = html.find("function carregarHistorico")
if idx != -1:
    fim = html.find("\n    }", idx) + 6
    print(html[idx:fim])
else:
    print("Função não encontrada.")

# 2. Mostra o trecho do HTML onde está a div do histórico
print("\n=== HTML DA DIV DE HISTÓRICO ===")
idx2 = html.find('id="historico-lista"')
if idx2 != -1:
    print(html[max(0, idx2-100):idx2+300])
else:
    print("Div não encontrada.")

# 3. Mostra o trecho do checkbox na função
print("\n=== TRECHO DO CHECKBOX NA FUNÇÃO ===")
idx3 = html.find('type="checkbox"')
if idx3 != -1:
    print(html[max(0, idx3-100):idx3+200])
else:
    print("Checkbox não encontrado.")
