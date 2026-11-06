import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Extrai o bloco completo da função DFC
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
if fim_dfc == -1:
    fim_dfc = idx_dfc + 5000
bloco_dfc = codigo[idx_dfc:fim_dfc]

print("=" * 70)
print("ESTRUTURA DA FUNÇÃO DFC")
print("=" * 70)
for i, linha in enumerate(bloco_dfc.split("\n")[:50], 1):
    print(f"{i:3}: {linha}")

print("\n" + "=" * 70)
print("ESTRUTURA DA FUNÇÃO BF")
print("=" * 70)
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
if fim_bf == -1:
    fim_bf = idx_bf + 5000
bloco_bf = codigo[idx_bf:fim_bf]

for i, linha in enumerate(bloco_bf.split("\n")[:60], 1):
    print(f"{i:3}: {linha}")
