import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra o início da função api_relatorio_v2
inicio = c.find('def api_relatorio_v2')
if inicio == -1:
    print("[ERRO] Função api_relatorio_v2 não encontrada.")
else:
    # Encontra o fim da função
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio + 10)
        if pos != -1 and pos < fim:
            fim = pos
    
    nova_funcao = '''def api_relatorio_v2(periodo_atual: str):
    import sqlite3, os, json, csv, io
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    # Calcula o período anterior (mesmo trimestre do ano anterior)
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
    
    def ler_csv(periodo_str):
        if not periodo_str:
            return []
        periodo_formatado = periodo_str.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")
        
        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
        
        if not os.path.exists(arquivo):
            return []
        
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            except:
                with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    linhas = f.readlines()
            
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break
            
            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1
            
            # Lê o cabeçalho para descobrir os meses
            meses_disponiveis = []
            for i in range(max(0, inicio_dados - 5), inicio_dados):
                if "JAN" in linhas[i].upper():
                    if ";" in linhas[i]:
                        partes_cab = linhas[i].strip().split(";")
                    else:
                        partes_cab = linhas[i].strip().split(",")
                    for p in partes_cab:
                        p_limpo = p.strip().upper()
                        if p_limpo in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]:
                            meses_disponiveis.append(p_limpo)
                    break
            
            if not meses_disponiveis:
                meses_disponiveis = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET"]
            
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
                
                # Valor total (última coluna)
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
            
            # Calcula os meses por centro
            meses_por_centro = []
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
                
                valores_meses = []
                for idx, mes in enumerate(meses_disponiveis, start=1):
                    if idx < len(partes):
                        v_str = partes[idx].strip().strip('"').replace(".", "").replace(",", ".")
                        try:
                            v = float(v_str)
                        except:
                            v = 0.0
                    else:
                        v = 0.0
                    valores_meses.append(v)
                
                meses_por_centro.append({"nome": nome, "meses": valores_meses})
            
            return {"centros": centros, "meses": meses_disponiveis, "meses_por_centro": meses_por_centro}
        except:
            return {"centros": [], "meses": [], "meses_por_centro": []}
    
    dados_atual = ler_csv(periodo_atual)
    dados_anterior = ler_csv(periodo_anterior)
    
    def processar(dados):
        if not dados or not dados.get("centros"):
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}
        
        centros = dados["centros"]
        total = sum(c.get("valor", 0) for c in centros)
        meses = dados["meses"]
        meses_por_centro = dados.get("meses_por_centro", [])
        
        # Calcula os totais mensais
        totais_meses = {m: 0.0 for m in meses}
        for item in meses_por_centro:
            for idx, m in enumerate(meses):
                if idx < len(item["meses"]):
                    totais_meses[m] += item["meses"][idx]
        
        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / len(meses) if meses and total > 0 else 0,
            "meses": totais_meses,
            "meses_disponiveis": meses
        }
    
    atual = processar(dados_atual)
    anterior = processar(dados_anterior) if dados_anterior and dados_anterior.get("centros") else {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}, "meses_disponiveis": []}
    
    return {
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }'''
    
    c = c[:inicio] + nova_funcao + c[fim:]
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Função api_relatorio_v2 reescrita com meses dinâmicos!")
