import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_fix_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga (para evitar conflito)
padrao = re.compile(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)
c = padrao.sub('', c)

nova_api = '''
@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    ano_atual = p_limpo.split("_")[0]
    ano_anterior = str(int(ano_atual) - 1)
    
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    # Arquivo do ano atual
    caminho_atual = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
    if not os.path.exists(caminho_atual):
        candidatos = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_atual}*.csv"))
        caminho_atual = candidatos[0] if candidatos else None
    
    # Arquivo do ano anterior
    caminho_anterior = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_anterior}_{p_limpo.split('_', 1)[1]}.csv")
    if not os.path.exists(caminho_anterior):
        candidatos_ant = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_anterior}*.csv"))
        caminho_anterior = candidatos_ant[0] if candidatos_ant else None
    
    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").replace("C", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0
    
    def extrair_dados(caminho):
        if not caminho or not os.path.exists(caminho): return {}
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            for row in csv.reader(f, delimiter=";"):
                linhas.append(row)
        
        def buscar_ativo(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 1 and termo in str(p[0]).upper():
                    return limpar(p[1])
            return 0.0
        
        def buscar_passivo(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 3 and termo in str(p[2]).upper():
                    return limpar(p[3])
            return 0.0
        
        def buscar_qualquer(termo):
            termo = termo.upper().strip()
            for p in linhas:
                if len(p) > 1 and termo in str(p[0]).upper():
                    return limpar(p[1])
                if len(p) > 3 and termo in str(p[2]).upper():
                    return limpar(p[3])
            return 0.0
        
        return {
            "ativo_circulante": buscar_ativo("ATIVO CIRCULANTE"),
            "caixa": buscar_ativo("CAIXA E EQUIVALENTES"),
            "creditos": buscar_ativo("CRÉDITOS A CURTO PRAZO"),
            "ativo_nao_circulante": buscar_ativo("ATIVO NÃO CIRCULANTE"),
            "imobilizado": buscar_ativo("IMOBILIZADO"),
            "passivo_circulante": buscar_passivo("PASSIVO CIRCULANTE"),
            "passivo_nao_circulante": buscar_passivo("PASSIVO NAO-CIRCULANTE"),
            "patrimonio_liquido": buscar_qualquer("PATRIMÔNIO LÍQUIDO"),
        }
    
    try:
        d_atual = extrair_dados(caminho_atual) if caminho_atual else {}
        d_anterior = extrair_dados(caminho_anterior) if caminho_anterior else {}
        
        resultado = {}
        for k in ["ativo_circulante", "caixa", "creditos", "ativo_nao_circulante", "imobilizado", "passivo_circulante", "passivo_nao_circulante", "patrimonio_liquido"]:
            resultado[k] = {
                "atual": d_atual.get(k, 0.0),
                "anterior": d_anterior.get(k, 0.0)
            }
        
        return {"erro": False, "dados": resultado}
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''

idx = c.find('@app.get("/analise_bp")')
if idx == -1: idx = c.find("if __name__")
if idx == -1: idx = len(c)

c = c[:idx] + nova_api + c[idx:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] API corrigida com valores do ano atual e anterior.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_fix_{ts}", back_path)
