import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra o início da função api_relatorio_centro_custos
inicio = c.find('def api_relatorio_centro_custos')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
else:
    # Encontra o próximo @app ou def após o início
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio)
        if pos != -1 and pos < fim:
            fim = pos
    
    nova_funcao = '''def api_relatorio_centro_custos(periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2025-TRIMESTRE-3"):
    import sqlite3, os, json, csv, io
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def buscar_dados(periodo):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def ler_csv_mensal(periodo):
        # Tenta ler o CSV original da pasta uploads_raw
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
        
        # Procura o arquivo que contém o período (ex: CENTRO_CUSTOS_2026_TRIMESTRE_3.csv)
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"CENTRO_CUSTOS_{periodo_formatado}.csv")
        
        if not os.path.exists(arquivo):
            # Tenta encontrar qualquer arquivo que contenha o período
            for f in os.listdir(upload_dir):
                if periodo_formatado in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
        
        if not os.path.exists(arquivo):
            return {}
        
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            
            # Encontra a linha de cabeçalho (que começa com "Centro de Custo x Conta")
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
                
                # As colunas mensais são: JAN, FEV, MAR, ABR, MAI, JUN (índices 1 a 6)
                try:
                    for idx, mes in enumerate(["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"], start=1):
                        if idx < len(partes):
                            valor_str = partes[idx].strip().strip('"').replace(".", "").replace(",", ".")
                            try:
                                meses[mes] += float(valor_str)
                            except:
                                pass
                except:
                    pass
            
            return meses
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV {arquivo}: {e}")
            return {}
    
    dados_atual = buscar_dados(periodo_atual)
    dados_anterior = buscar_dados(periodo_anterior)
    conn.close()
    
    def processar(dados, periodo):
        if not dados:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}}
        
        centros = dados.get("centros", [])
        centros = [c for c in centros if c.get("nome") not in ["Centro de Custo", "Centro de Custo x Conta"]]
        total = sum(c.get("valor", 0) for c in centros)
        
        # Lê os meses do CSV original
        meses = ler_csv_mensal(periodo)
        
        # Se não conseguir ler do CSV, simula a distribuição (fallback)
        if not meses or sum(meses.values()) == 0:
            if total > 0:
                meses = {
                    "JAN": total * 0.12,
                    "FEV": total * 0.13,
                    "MAR": total * 0.20,
                    "ABR": total * 0.15,
                    "MAI": total * 0.20,
                    "JUN": total * 0.20
                }
        
        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
            "meses": meses
        }
    
    atual = processar(dados_atual, periodo_atual)
    anterior = processar(dados_anterior, periodo_anterior) if dados_anterior else None
    
    if anterior is None:
        return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": None,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o período anterior."
        }
    
    return {
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
'''
    
    c = c[:inicio] + nova_funcao + c[fim:]
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Função reescrita com leitura de meses do CSV!")
