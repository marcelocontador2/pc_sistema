import os, csv, io

upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
arquivo = os.path.join(upload_dir, "COMPARATIVO_RECEITAS_2026_TRIMESTRE_3.csv")

print(f"Procurando: {arquivo}")
print(f"Existe? {os.path.exists(arquivo)}")

if not os.path.exists(arquivo):
    print(f"[ERRO] Arquivo não encontrado.")
else:
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except UnicodeDecodeError:
        with open(arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()
    
    print(f"\n=== PRIMEIRAS 30 LINHAS DO CSV ===")
    for i, linha in enumerate(linhas[:30]):
        print(f"{i+1}: {linha.strip()[:150]}")
    
    print(f"\nTotal de linhas: {len(linhas)}")
