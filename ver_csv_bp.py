import csv, os

pasta = "pc_storage/uploads_raw"
caminho = os.path.join(pasta, "BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv")

if not os.path.exists(caminho):
    print("[ERRO] CSV nao encontrado:", caminho)
else:
    print("=" * 70)
    print("ESTRUTURA DO CSV DO BP (primeiras 30 linhas)")
    print("=" * 70)
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for i, row in enumerate(leitor):
            if i >= 30:
                break
            # Mostra o numero da linha e as colunas separadas
            print(f"\nLinha {i+1}:")
            for j, col in enumerate(row):
                if col.strip():
                    print(f"  Coluna {j}: {repr(col.strip()[:80])}")
