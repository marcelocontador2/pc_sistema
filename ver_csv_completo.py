import csv, os

caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
if not os.path.exists(caminho):
    print("[ERRO] Arquivo nao encontrado.")
else:
    print("=" * 70)
    print("ESTRUTURA COMPLETA DO CSV (primeiras 40 linhas)")
    print("=" * 70)
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for i, row in enumerate(leitor):
            if i >= 40:
                break
            # Mostra o numero da linha e cada coluna (mesmo que vazia)
            colunas_formatadas = []
            for j, col in enumerate(row):
                if col.strip():
                    colunas_formatadas.append(f"Col{j}={repr(col.strip()[:50])}")
            if colunas_formatadas:
                print(f"Linha {i+1}: " + " | ".join(colunas_formatadas))
