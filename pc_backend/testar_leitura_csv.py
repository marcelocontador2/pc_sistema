import os, csv, io

def ler_csv_mensal(periodo):
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    periodo_formatado = periodo.replace("-", "_")
    arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")
    
    print(f"Procurando: {arquivo}")
    print(f"Existe? {os.path.exists(arquivo)}")
    
    if not os.path.exists(arquivo):
        for f in os.listdir(upload_dir):
            if periodo_formatado in f:
                arquivo = os.path.join(upload_dir, f)
                print(f"Encontrado alternativo: {arquivo}")
                break
    
    if not os.path.exists(arquivo):
        print("Arquivo não encontrado!")
        return {}
    
    try:
        try:
            with open(arquivo, "r", encoding="utf-8-sig") as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin-1") as f:
                linhas = f.readlines()
        
        inicio_dados = 0
        for i, linha in enumerate(linhas):
            if "Centro de Custo x Conta" in linha:
                inicio_dados = i + 1
                break
        
        if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
            inicio_dados += 1
        
        meses = {"JAN": 0, "FEV": 0, "MAR": 0, "ABR": 0, "MAI": 0, "JUN": 0}
        
        for linha in linhas[inicio_dados:]:
            if ";" in linha:
                partes = linha.strip().split(";")
            else:
                partes = linha.strip().split(",")
            
            if len(partes) < 7:
                continue
            
            nome = partes[0].strip().strip('"')
            if not nome or "TOTAL" in nome.upper() or "Centro de Custo" in nome:
                continue
            
            for idx, mes in enumerate(["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"], start=1):
                if idx < len(partes):
                    valor_str = partes[idx].strip().strip('"').replace(".", "").replace(",", ".")
                    try:
                        meses[mes] += float(valor_str)
                    except:
                        pass
        
        return meses
    except Exception as e:
        print(f"Erro: {e}")
        return {}

# Testa para o período anterior
print("=== TESTANDO 2025-TRIMESTRE-3 ===")
resultado = ler_csv_mensal("2025-TRIMESTRE-3")
print("Resultado:", resultado)
