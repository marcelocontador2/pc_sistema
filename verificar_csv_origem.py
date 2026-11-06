import os, glob

# 1. Localiza os CSVs originais do BF e DFC
pasta_uploads = os.path.join("pc_storage", "uploads_raw")
print("=" * 70)
print("ARQUIVOS CSV EM uploads_raw")
print("=" * 70)
for f in sorted(os.listdir(pasta_uploads))[:30]:
    if f.endswith(".csv"):
        print(f"  {f}")

# 2. Lê as primeiras linhas do CSV do DFC e BF
print("\n" + "=" * 70)
print("CONTEÚDO DOS CSVs (primeiras linhas)")
print("=" * 70)
for csv in ["DFC_2026_TRIMESTRE_3.csv", "BALANCO_FINANCEIRO_2026_TRIMESTRE_3.csv"]:
    caminho = os.path.join(pasta_uploads, csv)
    if os.path.exists(caminho):
        print(f"\n--- {csv} ---")
        with open(caminho, "r", encoding="utf-8", errors="replace") as f:
            for i, linha in enumerate(f.readlines()[:15]):
                print(f"  Linha {i+1}: {linha.strip()[:150]}")
    else:
        print(f"\n[AVISO] {csv} não encontrado.")
