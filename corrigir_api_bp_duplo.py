import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_duplo_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga do BP (para evitar conflito)
padrao = re.compile(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)
c = padrao.sub('', c)

nova_api = '''
@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    # Extrai o ano do periodo (ex: "2026-TRIMESTRE-3" -> "2026")
    ano_atual = p_limpo.split("_")[0]
    ano_anterior = str(int(ano_atual) - 1)
    
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    # Procura o arquivo do ano atual
    caminho_atual = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{p_limpo}.csv")
    if not os.path.exists(caminho_atual):
        # Tenta encontrar qualquer arquivo do ano atual
        candidatos = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_atual}*.csv"))
        if candidatos:
            caminho_atual = candidatos[0]
        else:
            return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    
    # Procura o arquivo do ano anterior (mesmo trimestre)
    caminho_anterior = os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_anterior}_{p_limpo.split('_', 1)[1]}.csv")
    if not os.path.exists(caminho_anterior):
        # Tenta encontrar qualquer arquivo do ano anterior
        candidatos_ant = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_anterior}*.csv"))
        caminho_anterior = candidatos_ant[0] if candidatos_ant else None
    
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
    
    def extrair_dados(caminho):
        if not caminho or not os.path.exists(caminho):
            return {}
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            leitor = csv.reader(f, delimiter=";")
            for row in leitor:
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
        dados_atual = extrair_dados(caminho_atual)
        dados_anterior = extrair_dados(caminho_anterior) if caminho_anterior else {}
        
        resultado = {}
        for k in dados_atual:
            resultado[k] = {
                "atual": dados_atual.get(k, 0.0),
                "anterior": dados_anterior.get(k, 0.0)
            }
        
        return {"erro": False, "dados": resultado}
    
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
    print("[OK] API da Analise BP corrigida para ler DOIS arquivos (atual e anterior).")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_duplo_{ts}", back_path)
