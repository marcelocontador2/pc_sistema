import os

upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"

print("=== Arquivos COMPARATIVO_DESPESAS encontrados ===")
encontrados = [f for f in os.listdir(upload_dir) if "COMPARATIVO_DESPESAS" in f.upper()]
for f in encontrados:
    print("  -", f)

if not encontrados:
    print("  [!!] Nenhum arquivo COMPARATIVO_DESPESAS encontrado!")
else:
    # Pega o mais recente e mostra as primeiras linhas
    arquivo = os.path.join(upload_dir, encontrados[0])
    print(f"\n=== Primeiras 10 linhas de: {encontrados[0]} ===")
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as fh:
            linhas = fh.readlines()
    except UnicodeDecodeError:
        with open(arquivo, "r", encoding="latin-1") as fh:
            linhas = fh.readlines()
    
    for i, linha in enumerate(linhas[:10]):
        print(f"  [{i}] {linha.rstrip()}")
    
    print(f"\nTotal de linhas: {len(linhas)}")
