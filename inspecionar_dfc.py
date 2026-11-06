with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Localiza a função DFC
inicio = None
for i, l in enumerate(linhas):
    if "def gerar_pdf_analise_dfc" in l:
        inicio = i
        break

if inicio:
    print("=== PRIMEIRAS 60 LINHAS DA FUNÇÃO DFC ===")
    for i in range(inicio, min(inicio + 60, len(linhas))):
        print(f"{i+1:4}: {linhas[i]}", end="")
