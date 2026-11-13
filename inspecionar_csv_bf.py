import os
import csv

pasta = os.path.join("pc_storage", "uploads_raw")
arquivo = None

for f in os.listdir(pasta):
    if "BALANCO_FINANCEIRO" in f.upper() and "2026" in f:
        arquivo = os.path.join(pasta, f)
        break

if arquivo:
    print(f"📄 Arquivo: {arquivo}")
    print("=" * 100)
    with open(arquivo, "r", encoding="latin-1") as f:
        leitor = csv.reader(f, delimiter=';')
        for i, linha in enumerate(leitor):
            if i >= 40: break
            # Mostra as primeiras 7 colunas de cada linha
            resumo = [str(c)[:30] for c in linha[:7]]
            print(f"Linha {i+1:2d}: {resumo}")
else:
    print("❌ Arquivo não encontrado.")
