import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra o início da função api_relatorio_centro_custos
inicio = c.find('def api_relatorio_centro_custos')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
else:
    # Encontra o fim da função
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio + 10)
        if pos != -1 and pos < fim:
            fim = pos
    
    nova_funcao = '''def api_relatorio_centro_custos(id: int = None, periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = None):
    import sqlite3, os, json, csv, io
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Calcula o período anterior automaticamente (mesmo trimestre do ano anterior)
    if not periodo_anterior:
        partes = periodo_atual.split("-")
        if len(partes) == 3:
            ano = int(partes[0])
            tipo = partes[1]
            valor = partes[2]
            periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    
    def ler_csv(periodo_str):
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
            
            return centros
        except:
            return []
    
    def buscar_historico(periodo_str):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo_str,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def processar(centros, periodo_str):
        if not centros:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}}
        
        total = sum(c.get("valor", 0) for c in centros)
        
        meses = {}
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
    
    centros_atual = ler_csv(periodo_atual)
    if not centros_atual:
        dados_banco = buscar_historico(periodo_atual)
        if dados_banco:
            centros_atual = dados_banco.get("centros", [])
    
    centros_anterior = ler_csv(periodo_anterior)
    if not centros_anterior:
        dados_banco_anterior = buscar_historico(periodo_anterior)
        if dados_banco_anterior:
            centros_anterior = dados_banco_anterior.get("centros", [])
    
    conn.close()
    
    atual = processar(centros_atual, periodo_atual)
    anterior = processar(centros_anterior, periodo_anterior) if centros_anterior else None
    
    if anterior is None or anterior["total"] == 0:
        return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": periodo_anterior,
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
    }'''
    
    c = c[:inicio] + nova_funcao + c[fim:]
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Função reescrita com cálculo automático do período anterior!")
