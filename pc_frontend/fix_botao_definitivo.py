import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_definitivo")

# Procura QUALQUER botao que tenha o texto "Gerar PDF" (independente da classe)
padrao = re.compile(r'(<button[^>]*>\s*Gerar PDF\s*</button>)', re.IGNORECASE)
match = padrao.search(s)

if match:
    # Insere o botao Exibir ao lado do Gerar PDF
    novo_botao = match.group(1) + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'
    s = s[:match.start()] + novo_botao + s[match.end():]
    print("OK: Botao 'Exibir' inserido ao lado do 'Gerar PDF'.")
else:
    # Se nao encontrar o Gerar PDF, tenta o Excluir
    padrao2 = re.compile(r'(<button[^>]*>\s*Excluir\s*</button>)', re.IGNORECASE)
    match2 = padrao2.search(s)
    if match2:
        novo_botao = match2.group(1) + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'
        s = s[:match2.start()] + novo_botao + s[match2.end():]
        print("OK: Botao 'Exibir' inserido ao lado do 'Excluir'.")
    else:
        # Fallback: insere no final da top-bar
        s = s.replace('</div>\n\n    <div class="filtros">', '<button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>\n    </div>\n\n    <div class="filtros">')
        print("OK: Botao 'Exibir' inserido no final da barra de botoes.")

# Garante que a funcao exibirNovo existe
if "function exibirNovo" not in s:
    print("AVISO: Funcao exibirNovo() nao encontrada. Verifique o arquivo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
