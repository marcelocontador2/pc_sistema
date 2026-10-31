import os
import csv
base = r"C:\Users\Marcelo Medeiros\pc_sistema"
pasta = os.path.join(base, "pc_storage", "uploads_raw")
print("--- Buscando CORRENTE no DFC ---")
for arquivo in os.listdir(pasta):
    if arquivo.upper().startswith("DFC_2026"):
        caminho = os.path.join(pasta, arquivo)
        with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
            leitor = csv.reader(f, delimiter=';')
            for i, linha in enumerate(leitor):
                if not linha: continue
                if "CORRENTE" in " ".join(linha).upper():
                    print(f"Linha {i}:")
                    for idx, col in enumerate(linha[:8]):
                        print(f"  Coluna {idx} = '{col}'")
                    print("-" * 30)
