import csv, os, glob

pasta = r"pc_storage/uploads_raw"
# Procura o arquivo do BP
arquivos = glob.glob(os.path.join(pasta, "BALANCO_PATRIMONIAL_2026*.csv"))
if not arquivos:
    print("[ERRO] Nenhum arquivo BALANCO_PATRIMONIAL_2026*.csv encontrado.")
else:
    caminho = arquivos[0]
    print(f"Analisando: {caminho}")
    print("=" * 70)
    
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for i, row in enumerate(leitor):
            if i >= 25:
                break
            # Mostra apenas as linhas que contêm os termos que buscamos
            linha_str = ";".join(row).upper()
            if any(termo in linha_str for termo in ["ATIVO CIRCULANTE", "CAIXA", "CREDITOS", "IMOBILIZADO", "PASSIVO CIRCULANTE", "PATRIMONIO"]):
                print(f"\nLinha {i+1}:")
                for j, col in enumerate(row):
                    if col.strip():
                        print(f"  Coluna {j}: {repr(col.strip()[:80])}")
