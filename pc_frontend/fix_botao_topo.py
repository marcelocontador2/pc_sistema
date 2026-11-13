import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_topo")

# 1. Remove o botao "Exibir" do lugar errado (dentro dos filtros)
s = re.sub(r'<button[^>]*onclick="exibirNovo\(\)"[^>]*>Exibir</button>', '', s, flags=re.DOTALL)

# 2. Adiciona o botao "Exibir" no topo, ao lado do "Gerar PDF"
ancora = '<button class="btn btn-pdf" onclick="gerarPDFHistorico()">Gerar PDF</button>'
if ancora not in s:
    ancora = '<button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>'
    if ancora not in s:
        ancora = '<button class="btn btn-azul" onclick="gerarPDFHistorico()">Gerar PDF</button>'

novo_botao = ancora + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'

if ancora in s:
    s = s.replace(ancora, novo_botao, 1)
    print("OK: Botao 'Exibir' movido para o topo, ao lado do 'Gerar PDF'.")
else:
    # Fallback: adiciona ao lado do botao Excluir
    ancora2 = '<button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir</button>'
    if ancora2 in s:
        s = s.replace(ancora2, ancora2 + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>', 1)
        print("OK: Botao 'Exibir' adicionado ao lado do 'Excluir'.")
    else:
        print("ERRO: Nenhuma ancora encontrada no topo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
