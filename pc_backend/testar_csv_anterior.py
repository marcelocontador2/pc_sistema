import os, csv, io

upload_dir = os.path.join(os.getcwd(), "..", "pc_storage", "uploads_raw")
arquivo = os.path.join(upload_dir, "CENTRO_CUSTOS_2025_TRIMESTRE_3.csv")
print(f"Arquivo existe? {os.path.exists(arquivo)}")

if os.path.exists(arquivo):
    with open(arquivo, "r", encoding="utf-8-sig") as f:
        linhas = f.readlines()
    
    inicio_dados = 0
    for i, linha in enumerate(linhas):
        if "Centro de Custo x Conta" in linha:
            inicio_dados = i + 1
            break
    
    if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
        inicio_dados += 1
    
    print(f"Início dos dados: linha {inicio_dados + 1}")
    print("Primeiras 5 linhas de dados:")
    for linha in linhas[inicio_dados:inicio_dados+5]:
        print(f"  {linha.strip()[:100]}")
