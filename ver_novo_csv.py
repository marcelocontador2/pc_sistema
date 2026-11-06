import csv, os

caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
if not os.path.exists(caminho):
    print("[ERRO] Arquivo nao encontrado.")
else:
    print("=" * 70)
    print("NOVA ESTRUTURA DO CSV (primeiras 20 linhas)")
    print("=" * 70)
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for i, row in enumerate(leitor):
            if i >= 20:
                break
            colunas = [f"Col{j}={repr(c.strip()[:40])}" for j, c in enumerate(row) if c.strip()]
            if colunas:
                print(f"Linha {i+1}: " + " | ".join(colunas))
