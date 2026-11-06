import re

arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

with open("trecho_desenho_bp.txt", "w", encoding="utf-8") as out:
    for i, linha in enumerate(linhas):
        if "passivo_total" in linha and i > 1086: # Pula a parte onde ele busca o valor
            # Mostra o contexto de 5 linhas antes e depois
            inicio = max(0, i - 5)
            fim = min(len(linhas), i + 5)
            out.write(f"--- Linha {i+1} ---\n")
            for j in range(inicio, fim):
                marcador = ">>> " if j == i else "    "
                out.write(f"{marcador}{linhas[j]}")
            out.write("\n")

print("[OK] Trecho de desenho do PDF extraído para 'trecho_desenho_bp.txt'.")
