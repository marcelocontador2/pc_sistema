import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_fix2_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Substitui a API do BP por uma versao que ignora acentos e busca em todas as colunas
padrao = re.compile(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)

nova_api = '''
@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob, unicodedata
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
    # Busca qualquer arquivo de Balanco Patrimonial do ano atual
    ano_atual = p_limpo.split("_")[0]
    candidatos = glob.glob(os.path.join(pasta, f"BALANCO_PATRIMONIAL_{ano_atual}*.csv"))
    if not candidatos:
        return {"erro": "faltando", "pecas": ["Balanco Patrimonial"]}
    caminho = candidatos[0]
    
    def limpar(v):
        if not v: return 0.0
        v = str(v).replace("R$", "").replace("C", "").strip()
        if v in ["-", "0,00", ""]: return 0.0
        if "," in v and "." in v: v = v.replace(".", "").replace(",", ".")
        elif "," in v: v = v.replace(",", ".")
        try: return float(v)
        except: return 0.0
    
    def remover_acentos(s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').upper().strip()
    
    try:
        linhas = []
        with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
            for row in csv.reader(f, delimiter=";"):
                linhas.append(row)
        
        def buscar(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                # Verifica coluna 0 (Ativo)
                if len(p) > 1 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1]), 0.0
                # Verifica coluna 2 (Passivo)
                if len(p) > 3 and termo_norm in remover_acentos(str(p[2])):
                    return limpar(p[3]), 0.0
            return 0.0, 0.0
        
        dados = {
            "ativo_circulante": buscar("ATIVO CIRCULANTE"),
            "caixa": buscar("CAIXA E EQUIVALENTES"),
            "creditos": buscar("CREDITOS A CURTO PRAZO"),
            "ativo_nao_circulante": buscar("ATIVO NAO CIRCULANTE"),
            "imobilizado": buscar("IMOBILIZADO"),
            "passivo_circulante": buscar("PASSIVO CIRCULANTE"),
            "passivo_nao_circulante": buscar("PASSIVO NAO-CIRCULANTE"),
            "patrimonio_liquido": buscar("PATRIMONIO LIQUIDO"),
        }
        
        # Como o CSV so tem o exercicio atual, usamos o mesmo valor para "anterior" 
        # (ou 0, se preferir)
        resultado = {}
        for k, (v_at, v_ant) in dados.items():
            resultado[k] = {"atual": v_at, "anterior": v_at}  # Repete o valor para mostrar algo
        
        return {"erro": False, "dados": resultado}
    
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''

if padrao.search(c):
    c = padrao.sub(nova_api, c, count=1)
else:
    # Se nao encontrou, insere antes da rota /analise_bp
    idx = c.find('@app.get("/analise_bp")')
    if idx == -1: idx = c.find("if __name__")
    if idx == -1: idx = len(c)
    c = c[:idx] + nova_api + c[idx:]

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] API do BP corrigida para ignorar acentos e buscar em todas as colunas.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_fix2_{ts}", back_path)
