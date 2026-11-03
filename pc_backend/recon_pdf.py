import re

c = open("main.py", encoding="utf-8-sig").read()

print("=" * 60)
print("ROTAS RELACIONADAS A PDF DE RECEITAS")
print("=" * 60)

for m in re.finditer(r'@app\.(get|post)\(["\'](/gerar_pdf_comparativo_receitas[^"\']*)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c):
    print(f"\nRota: {m.group(2)}")
    inicio = m.end()
    prox = re.search(r'\n@app\.', c[inicio:])
    fim = inicio + prox.start() if prox else len(c)
    corpo = c[inicio:fim]
    print(corpo[:2000])

print("\n" + "=" * 60)
print("ARQUIVO relatorio_comparativo_receitas_v2.html")
print("=" * 60)
import os
caminho = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend\relatorio_comparativo_receitas_v2.html"
if os.path.exists(caminho):
    print("Arquivo encontrado. Primeiras 50 linhas:")
    with open(caminho, encoding="utf-8-sig") as f:
        for i, linha in enumerate(f.readlines()[:50]):
            print(f"{i+1}: {linha.rstrip()}")
else:
    print("Arquivo NÃO encontrado no caminho:", caminho)
