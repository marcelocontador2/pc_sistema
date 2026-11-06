import re

c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Procura a palavra "Excluir" ou "excluir"
idx = c.find("Excluir")
if idx == -1:
    idx = c.find("excluir")

if idx != -1:
    print("Trecho ao redor do botão Excluir no index.html:")
    print(repr(c[max(0, idx-300):idx+200]))
else:
    print("Botão Excluir não encontrado no index.html.")
