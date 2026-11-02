import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove a rota antiga (simulada) e substitui por uma que lê o CSV
padrao = r'@app\.get\("/api/centro_custos/\{periodo\}"\).*?return \{\s*"erro": False,.*?\}'

nova_rota = '''@app.get("/api/centro_custos/{periodo}")
def api_centro_custos(periodo: str):
    import os, csv, io
    
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    periodo_formatado = periodo.replace("-", "_")
    arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")
    
    if not os.path.exists(arquivo):
        for f in os.listdir(upload_dir):
            if periodo_formatado in f:
                arquivo = os.path.join(upload_dir, f)
                break
    
    if not os.path.exists(arquivo):
        return {"erro": True, "mensagem": f"Arquivo para o período {periodo} não encontrado."}
    
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
        
        centros = []
        for linha in linhas[inicio_dados:]:
            if ";" in linha:
                partes = linha.strip().split(";")
            else:
                partes = linha.strip().split(",")
            
            if len(partes) < 2:
                continue
            
            nome = partes[0].strip().strip('"')
            if not nome or "TOTAL" in nome.upper() or "Centro de Custo" in nome:
                continue
            
            # Pega o último valor numérico válido (coluna Realizado)
            valor = 0.0
            for parte in reversed(partes):
                parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                try:
                    valor = float(parte_limpa)
                    if valor > 0:
                        break
                except:
                    continue
            
            centros.append({"nome": nome, "valor": valor})
        
        return {"erro": False, "periodo": periodo, "centros": centros}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_rota, c, flags=re.DOTALL)
    print("[OK] Rota /api/centro_custos/{periodo} alterada para ler o CSV real!")
else:
    print("[AVISO] Rota antiga não encontrada. Tentando abordagem alternativa...")
    # Tenta encontrar qualquer rota que comece com /api/centro_custos/{periodo}
    inicio = c.find('@app.get("/api/centro_custos/{periodo}")')
    if inicio != -1:
        fim = c.find('@app.', inicio + 10)
        if fim == -1: fim = len(c)
        c = c[:inicio] + nova_rota + '\n\n' + c[fim:]
        print("[OK] Rota substituída por leitura de CSV!")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
