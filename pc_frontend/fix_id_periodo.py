import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui a busca do periodo pelo ID correto ('val')
antigo = "const periodo = document.getElementById('periodo') ? document.getElementById('periodo').value : '3';"
novo = "const periodo = document.getElementById('val') ? document.getElementById('val').value : '3';"

if antigo in js:
    js = js.replace(antigo, novo)
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK: O JavaScript agora busca o ID 'val' para o periodo.")
else:
    print("AVISO: O trecho antigo nao foi encontrado no dmpl_functions.js.")

# Atualiza tambem o script inline no HTML
path_html = "analise_dmpl.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

# O script inline deve ser atualizado com o conteudo do js novo
padrao_inline = re.compile(r'<script>\s*// VERSAO NOVA DO SCRIPT.*?</script>', re.DOTALL)
novo_inline = f'<script>\n// VERSAO NOVA DO SCRIPT\n{js}\n</script>'

if padrao_inline.search(html):
    html = padrao_inline.sub(novo_inline, html)
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK: Script inline no HTML atualizado com a correcao.")
else:
    print("AVISO: Script inline nao encontrado para atualizar.")
