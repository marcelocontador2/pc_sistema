import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_dfc_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se a API ja existe
if '/api/analise_dfc' in c:
    print("[AVISO] A API /api/analise_dfc ja existe no main.py.")
else:
    # Procura a rota /analise_dfc para inserir a API antes
    idx = c.find('@app.get("/analise_dfc")')
    if idx == -1:
        print("[ERRO] Rota /analise_dfc nao encontrada.")
        exit(1)
    
    # Monta a API (que le o CSV e retorna os dados no formato esperado)
    api_code = '''
# ============================================================
# API DA ANALISE DFC (le o CSV e retorna os dados)
# ============================================================

@app.get("/api/analise_dfc/{periodo}")
async def api_analise_dfc(periodo: str):
    import csv, os
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    caminho = os.path.join(pasta, f"DFC_{p_limpo}.csv")
    
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["DFC"]}
    
    def limpar(v):
        if not v:
            return 0.0
        v = str(v).replace("R$", "").strip()
        if v in ["-", "0,00", ""]:
            return 0.0
        if "," in v and "." in v:
            v = v.replace(".", "").replace(",", ".")
        elif "," in v:
            v = v.replace(",", ".")
        try:
            return float(v)
        except Exception:
            return 0.0
    
    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            leitor = csv.reader(f, delimiter=";")
            for row in leitor:
                linhas.append(row)
        
        def buscar(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 0 and termo in str(p[0]).upper():
                    return p
                if len(p) > 3 and termo in str(p[3]).upper():
                    return p
            return None
        
        def val(p, idx):
            if p and len(p) > idx:
                return limpar(p[idx])
            return 0.0
        
        # Blocos
        def achar_idx(termo, inicio=0):
            termo = termo.upper().strip()
            for i in range(inicio, len(linhas)):
                p = linhas[i]
                if len(p) > 0 and termo in str(p[0]).upper():
                    return i
                if len(p) > 3 and termo in str(p[3]).upper():
                    return i
            return -1
        
        idx_oper = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERA")
        idx_invest = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO")
        idx_financ = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO")
        idx_apuracao = achar_idx("APURA")
        
        if idx_oper == -1 or idx_invest == -1 or idx_financ == -1 or idx_apuracao == -1:
            return {"erro": "estrutura", "mensagem": "Nao foi possivel localizar os blocos da DFC no CSV."}
        
        def buscar_bloco(bloco, termo):
            termo = termo.upper().strip()
            for p in bloco:
                if len(p) > 0 and termo in str(p[0]).upper():
                    return p
                if len(p) > 3 and termo in str(p[3]).upper():
                    return p
            return None
        
        # Operacional
        linhas_oper = linhas[idx_oper:idx_invest]
        l_ing_oper = buscar_bloco(linhas_oper, "INGRESSOS")
        l_desemb_oper = buscar_bloco(linhas_oper, "DESEMBOLSOS")
        l_liq_oper = buscar_bloco(linhas_oper, "FLUXO DE CAIXA L")
        
        # Investimento
        linhas_invest = linhas[idx_invest:idx_financ]
        l_ing_invest = buscar_bloco(linhas_invest, "INGRESSOS")
        l_desemb_invest = buscar_bloco(linhas_invest, "DESEMBOLSOS")
        l_liq_invest = buscar_bloco(linhas_invest, "FLUXO DE CAIXA L")
        
        # Financiamento
        linhas_financ = linhas[idx_financ:idx_apuracao]
        l_ing_financ = buscar_bloco(linhas_financ, "INGRESSOS")
        l_desemb_financ = buscar_bloco(linhas_financ, "DESEMBOLSOS")
        l_liq_financ = buscar_bloco(linhas_financ, "FLUXO DE CAIXA L")
        
        # Apuracao
        linhas_apuracao = linhas[idx_apuracao:]
        l_geracao = buscar_bloco(linhas_apuracao, "GERA")
        l_caixa_inicial = buscar_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA INICIAL")
        l_caixa_final = buscar_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA FINAL")
        
        dados = {
            "operacional": {
                "ingressos": {"atual": val(l_ing_oper, 3), "anterior": val(l_ing_oper, 4)},
                "desembolsos": {"atual": val(l_desemb_oper, 3), "anterior": val(l_desemb_oper, 4)},
                "liquido": {"atual": val(l_liq_oper, 3), "anterior": val(l_liq_oper, 4)},
            },
            "investimento": {
                "ingressos": {"atual": val(l_ing_invest, 3), "anterior": val(l_ing_invest, 4)},
                "desembolsos": {"atual": val(l_desemb_invest, 3), "anterior": val(l_desemb_invest, 4)},
                "liquido": {"atual": val(l_liq_invest, 3), "anterior": val(l_liq_invest, 4)},
            },
            "financiamento": {
                "ingressos": {"atual": val(l_ing_financ, 3), "anterior": val(l_ing_financ, 4)},
                "desembolsos": {"atual": val(l_desemb_financ, 3), "anterior": val(l_desemb_financ, 4)},
                "liquido": {"atual": val(l_liq_financ, 3), "anterior": val(l_liq_financ, 4)},
            },
            "caixa": {
                "geracao": {"atual": val(l_geracao, 3), "anterior": val(l_geracao, 4)},
                "inicial": {"atual": val(l_caixa_inicial, 3), "anterior": val(l_caixa_inicial, 4)},
                "final": {"atual": val(l_caixa_final, 3), "anterior": val(l_caixa_final, 4)},
            }
        }
        return {"erro": False, "dados": dados}
    
    except Exception as e:
        print(f"[DFC] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''
    
    # Insere a API antes da rota da pagina
    c = c[:idx] + api_code + c[idx:]
    open(back_path, "w", encoding="utf-8").write(c)
    
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] API /api/analise_dfc criada e sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_api_dfc_{ts}", back_path)
        print("[OK] Backup restaurado.")
