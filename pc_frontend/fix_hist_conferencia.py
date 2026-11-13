import re, shutil

path = "conferencia.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_hist_conferencia")

# Corrige o ID do elemento na funcao carregarHistorico
antigo = "document.getElementById('lista-historico').innerHTML = html;"
novo = "document.getElementById('historico-lista').innerHTML = html;"

if antigo in s:
    s = s.replace(antigo, novo, 1)
    print("OK: ID 'lista-historico' corrigido para 'historico-lista'.")
else:
    print("AVISO: Trecho nao encontrado.")

# Tambem verifica se o elemento tem o ID correto no HTML
if 'id="historico-lista"' not in s and 'id="lista-historico"' in s:
    s = s.replace('id="lista-historico"', 'id="historico-lista"')
    print("OK: ID do elemento HTML corrigido para 'historico-lista'.")
elif 'id="historico-lista"' in s:
    print("OK: Elemento HTML ja tem o ID 'historico-lista'.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
