import re

arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Procura a linha que contém a string do Total do Passivo
indice_alvo = -1
for i, linha in enumerate(linhas):
    if "TOTAL DO PASSIVO" in linha.upper():
        indice_alvo = i
        break

with open("trecho_pdf_bp.txt", "w", encoding="utf-8") as out:
    if indice_alvo != -1:
        inicio = max(0, indice_alvo - 30)
        fim = min(len(linhas), indice_alvo + 30)
        out.write(f"--- TRECHO ENCONTRADO NA LINHA {indice_alvo + 1} ---\n\n")
        for i in range(inicio, fim):
            marcador = ">>> " if i == indice_alvo else "    "
            out.write(f"{marcador}{linhas[i]}")
    else:
        out.write("Não encontrei 'TOTAL DO PASSIVO' no arquivo main.py.\n")
        out.write("Procurando por 'BALANCO PATRIMONIAL'...\n\n")
        for i, linha in enumerate(linhas):
            if "BALANCO PATRIMONIAL" in linha.upper() or "ANALISE BP" in linha.upper():
                out.write(f"Linha {i+1}: {linha}")

print("[OK] Trecho gerado no arquivo trecho_pdf_bp.txt")
