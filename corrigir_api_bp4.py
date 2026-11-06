import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp4_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga (se existir)
c = re.sub(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', '', c, flags=re.DOTALL)
# Também remove se estiver em outro lugar (fallback)
c = re.sub(r'# API DA ANALISE BP.*?raise HTTPException\(status_code=500, detail=str\(e\)\)', '', c, flags=re.DOTALL)

nova_api = '''
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
        v = str(v).replace("R$", "").replace("C", "").strip()
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
        
        # O CSV tem 4 colunas:
        # Coluna 0 = Especificacao do Ativo, Coluna 1 = Valor do Ativo
        # Coluna 2 = Especificacao do Passivo, Coluna 3 = Valor do Passivo
        
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
        
        # Como o CSV so tem o exercicio atual, usamos o mesmo valor para "anterior" 
        # (ou 0, se preferir)
        dados = {
            "ativo_circulante": {"atual": buscar_ativo("ATIVO CIRCULANTE"), "anterior": 0.0},
            "caixa": {"atual": buscar_ativo("CAIXA E EQUIVALENTES"), "anterior": 0.0},
            "creditos": {"atual": buscar_ativo("CRÉDITOS A CURTO PRAZO"), "anterior": 0.0},
            "ativo_nao_circulante": {"atual": buscar_ativo("ATIVO NÃO CIRCULANTE"), "anterior": 0.0},
            "imobilizado": {"atual": buscar_ativo("IMOBILIZADO"), "anterior": 0.0},
            "passivo_circulante": {"atual": buscar_passivo("PASSIVO CIRCULANTE"), "anterior": 0.0},
            "passivo_nao_circulante": {"atual": buscar_passivo("PASSIVO NAO-CIRCULANTE"), "anterior": 0.0},
            "patrimonio_liquido": {"atual": buscar_qualquer("PATRIMÔNIO LÍQUIDO"), "anterior": 0.0},
        }
        
        return {"erro": False, "dados": dados}
    
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''

# Insere a API antes da rota /analise_bp
idx = c.find('@app.get("/analise_bp")')
if idx == -1:
    idx = c.find("if __name__")
if idx == -1:
    idx = len(c)

c = c[:idx] + nova_api + c[idx:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] API da Analise BP corrigida para a estrutura real do CSV (4 colunas).")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp4_{ts}", back_path)
