import os

csv_dfc = os.path.join("pc_storage", "uploads_raw", "DFC_2026_TRIMESTRE_3.csv")

# Lê os bytes crus da linha 9
with open(csv_dfc, "rb") as f:
    linhas = f.readlines()
    
if len(linhas) > 9:
    linha9 = linhas[8]  # linha 9 (0-indexed = 8)
    print(f"Linha 9 (bytes): {linha9[:100]}")
    print()
    print(f"Linha 9 (hex):   {linha9[:100].hex()}")
    print()
    try:
        print(f"Linha 9 (UTF-8):   {linha9.decode('utf-8')[:100]}")
    except UnicodeDecodeError as e:
        print(f"[UTF-8] Erro: {e}")
    try:
        print(f"Linha 9 (Latin-1): {linha9.decode('latin-1')[:100]}")
    except Exception as e:
        print(f"[Latin-1] Erro: {e}")
    try:
        print(f"Linha 9 (cp1252):  {linha9.decode('cp1252')[:100]}")
    except Exception as e:
        print(f"[cp1252] Erro: {e}")
