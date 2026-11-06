import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp2_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga (se existir) para recriar limpa
padrao = re.compile(r'# =+\s*\n# API DA ANALISE BP.*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)
c = padrao.sub('', c)

nova_api = '''
# ============================================================
# API DA ANALISE BP (Balanco Patrimonial)
# ============================================================

@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    caminho = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
    
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    
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
                if len(p) > 2 and termo in str(p[0]).upper():
                    return limpar(p[1]), limpar(p[2])
                if len(p) > 4 and termo in str(p[3]).upper():
                    return limpar(p[4]), limpar(p[5])
            return 0.0, 0.0
        
        # Contas exatas do print (convertendo para milhares no frontend)
        dados = {
            "ativo_circulante": buscar("ATIVO CIRCULANTE"),
            "caixa": buscar("CAIXA E EQUIVALENTES"),
            "creditos": buscar("CREDITOS A CURTO PRAZO"),
            "ativo_nao_circulante": buscar("ATIVO NAO CIRCULANTE"),
            "imobilizado": buscar("IMOBILIZADO"),
            "passivo_circulante": buscar("PASSIVO CIRCULANTE"),
            "passivo_nao_circulante": buscar("PASSIVO NAO CIRCULANTE"),
            "patrimonio_liquido": buscar("PATRIMONIO LIQUIDO"),
        }
        
        # Converte tuplas para {atual, anterior}
        resultado = {}
        for k, (v_at, v_ant) in dados.items():
            resultado[k] = {"atual": v_at, "anterior": v_ant}
        
        return {"erro": False, "dados": resultado}
    
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''

# Insere a nova API antes da rota /analise_bp
idx = c.find('@app.get("/analise_bp")')
if idx == -1:
    idx = c.find("if __name__")
if idx == -1:
    idx = len(c)

c = c[:idx] + nova_api + c[idx:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] API da Analise BP reescrita com os campos exatos do print.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp2_{ts}", back_path)
