import os
import glob

# Procura arquivos CSV na pasta de uploads
folder = r"pc_storage\uploads_raw"
arquivos = glob.glob(os.path.join(folder, "*.csv"))

for arq in arquivos:
    # Foca nos arquivos de Balanço Patrimonial
    if "BP" in os.path.basename(arq).upper() or "BALANCO" in os.path.basename(arq).upper() or "PATRIMONIAL" in os.path.basename(arq).upper():
        print(f"\n--- Arquivo: {os.path.basename(arq)} ---")
        # Tenta ler com encoding latino-1, comum em arquivos do Excel
        with open(arq, "r", encoding="latin-1", errors="ignore") as f:
            for linha in f:
                if "SUPERAVIT" in linha.upper() or "FINANCEIRO" in linha.upper() or "CAIXA" in linha.upper() or "CREDITO" in linha.upper():
                    print(linha.strip())
