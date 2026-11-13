import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui o ID errado 'historico-lista' pelo correto 'lista-historico' dentro do script
s = s.replace("getElementById('historico-lista')", "getElementById('lista-historico')")

# Salva o arquivo
with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: ID 'historico-lista' corrigido para 'lista-historico' no JavaScript!")
