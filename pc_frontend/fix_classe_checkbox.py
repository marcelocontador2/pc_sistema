import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Corrige a classe dentro da funcao exibirSelecionado de 'check-historico' para 'check-hist'
s = s.replace("document.querySelector('.check-historico:checked')", "document.querySelector('.check-hist:checked')")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: Classe do checkbox corrigida na funcao exibirSelecionado!")
