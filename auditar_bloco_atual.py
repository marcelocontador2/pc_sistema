import re

c = open(r"pc_frontend\relatorio_comparativo_receitas_v2.html", encoding='utf-8').read()

print("=" * 70)
print("AUDITORIA: BLOCO DE GRUPOS NO ARQUIVO")
print("=" * 70)

inicio = c.find('let htmlGrupos')
fim = c.find("document.getElementById('lista-grupos').innerHTML", inicio)

if inicio != -1 and fim != -1:
    bloco = c[inicio:fim]
    print(bloco)
else:
    print("[ERRO] Bloco não encontrado.")
