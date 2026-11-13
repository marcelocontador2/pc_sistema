import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_final")

# Procura qualquer botao que tenha o texto "Verificar" e adiciona o novo botao ao lado
padrao = re.compile(r'(<button[^>]*>Verificar</button>)', re.IGNORECASE)
match = padrao.search(s)

if match:
    novo_botao = match.group(1) + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'
    s = s[:match.start()] + novo_botao + s[match.end():]
    print("OK: Botao 'Exibir' adicionado ao lado do 'Verificar'.")
else:
    # Se nao encontrar, procura o botao de salvar como ancora
    padrao2 = re.compile(r'(<button[^>]*>Confirmar e Salvar</button>)', re.IGNORECASE)
    match2 = padrao2.search(s)
    if match2:
        novo_botao = '<button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>\n        ' + match2.group(1)
        s = s[:match2.start()] + novo_botao + s[match2.end():]
        print("OK: Botao 'Exibir' adicionado ao lado do 'Confirmar e Salvar'.")
    else:
        print("ERRO: Nenhuma ancora encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
