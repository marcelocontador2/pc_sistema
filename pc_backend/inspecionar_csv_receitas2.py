import os

upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
arquivo = os.path.join(upload_dir, "COMPARATIVO_RECEITAS_2026_TRIMESTRE_3.csv")

try:
    with open(arquivo, "r", encoding="utf-8-sig") as f:
        linhas = f.readlines()
except UnicodeDecodeError:
    with open(arquivo, "r", encoding="latin-1") as f:
        linhas = f.readlines()

print("=== LINHAS 30 A 100 ===")
for i in range(30, min(100, len(linhas))):
    print(f"{i+1}: {linhas[i].strip()[:150]}")
