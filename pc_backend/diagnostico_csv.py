import os

# Caminho do arquivo de 2025
upload_dir = os.path.join(os.getcwd(), "..", "pc_storage", "uploads_raw")
arquivo = os.path.join(upload_dir, "CENTRO_CUSTOS_2025_TRIMESTRE_3.csv")

print(f"1. Arquivo existe? {os.path.exists(arquivo)}")
print(f"   Caminho: {arquivo}")

if os.path.exists(arquivo):
    # Tenta ler como UTF-8
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
        print(f"2. Leu como UTF-8? SIM ({len(linhas)} linhas)")
    except Exception as e:
        print(f"2. Leu como UTF-8? NÃO ({e})")
        try:
            with open(arquivo, "r", encoding="latin-1") as f:
                linhas = f.readlines()
            print(f"3. Leu como ANSI? SIM ({len(linhas)} linhas)")
        except Exception as e2:
            print(f"3. Leu como ANSI? NÃO ({e2})")
            linhas = []
    
    # Mostra as primeiras 15 linhas
    if linhas:
        print("\n=== PRIMEIRAS 15 LINHAS ===")
        for i, linha in enumerate(linhas[:15]):
            print(f"{i+1}: {linha.strip()[:120]}")
        
        # Encontra o cabeçalho
        inicio = None
        for i, linha in enumerate(linhas):
            if "Centro de Custo x Conta" in linha:
                inicio = i + 1
                break
        
        if inicio:
            print(f"\n4. Cabeçalho encontrado na linha {inicio}")
            print(f"   Próxima linha: {linhas[inicio].strip()[:120]}")
            
            # Tenta processar os dados
            if "COFEN/BR" in linhas[inicio]:
                inicio += 1
            
            print(f"5. Início dos dados: linha {inicio + 1}")
            print("   Primeiras 3 linhas de dados:")
            for linha in linhas[inicio:inicio+3]:
                print(f"   {linha.strip()[:120]}")
        else:
            print("\n4. Cabeçalho 'Centro de Custo x Conta' NÃO encontrado!")
    else:
        print("Não foi possível ler o arquivo.")
else:
    print("Arquivo não existe.")
