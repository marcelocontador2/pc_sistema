path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui "function exibirSelecionado() {" por "async function exibirSelecionado() {"
antigo = "function exibirSelecionado() {"
novo = "async function exibirSelecionado() {"

if antigo in s:
    s = s.replace(antigo, novo, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    print("OK: 'async' adicionado com sucesso na funcao exibirSelecionado!")
else:
    print("AVISO: Nao encontrei 'function exibirSelecionado() {' no arquivo. Ja pode estar com async.")
