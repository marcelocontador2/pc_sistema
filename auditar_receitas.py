with open(r"pc_frontend\analise_comparativo_receitas.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mostra o trecho onde está o botão de excluir
print("=== TRECHO DO BOTÃO DE EXCLUIR ===")
idx = html.find("Excluir Selecionado")
if idx != -1:
    inicio = max(0, idx - 300)
    fim = min(len(html), idx + 300)
    print(html[inicio:fim])
else:
    print("Botão 'Excluir Selecionado' não encontrado.")

# 2. Mostra o trecho da função excluir (se existir)
print("\n=== TRECHO DA FUNÇÃO DE EXCLUSÃO ===")
idx2 = html.find("function excluirSelecionado")
if idx2 != -1:
    inicio2 = idx2
    fim2 = min(len(html), idx2 + 800)
    print(html[inicio2:fim2])
else:
    print("Função 'excluirSelecionado' não encontrada.")

# 3. Mostra o trecho da renderização do histórico (onde os checkboxes são criados)
print("\n=== TRECHO DA RENDERIZAÇÃO DO HISTÓRICO ===")
idx3 = html.find("lista-historico") 
if idx3 == -1:
    idx3 = html.find("lista_historico")
if idx3 != -1:
    inicio3 = max(0, idx3 - 200)
    fim3 = min(len(html), idx3 + 1500)
    print(html[inicio3:fim3])
else:
    print("Elemento de histórico não encontrado.")
