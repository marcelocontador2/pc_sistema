import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_final_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

padrao = re.compile(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)

nova_api = '''
@app.get("/api/analise_bp/{periodo}")
async def api_analise_bp(periodo: str):
    import csv, os, glob, unicodedata
    from fastapi import HTTPException
    
    p_limpo = periodo.replace("-", "_")
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    
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
                # Ativo: coluna 0, valor na coluna 1
                if len(p) > 1 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1])
                # Passivo: coluna 2, valor na coluna 3
                if len(p) > 3 and termo_norm in remover_acentos(str(p[2])):
                    return limpar(p[3])
            return 0.0
        
        dados = {
            "ativo_circulante": buscar("ATIVO CIRCULANTE"),
            "caixa": buscar("CAIXA E EQUIVALENTES"),
            "creditos": buscar("CREDITOS A CURTO PRAZO"),
            "ativo_nao_circulante": buscar("ATIVO NAO CIRCULANTE"),
            "imobilizado": buscar("IMOBILIZADO"),
            "passivo_circulante": buscar("PASSIVO CIRCULANTE"),
            "passivo_nao_circulante": buscar("PASSIVO NAO-CIRCULANTE"),
            "patrimonio_liquido": buscar("RESULTADOS ACUMULADOS"),  # PL = Resultados Acumulados
        }
        
        resultado = {}
        for k, v in dados.items():
            resultado[k] = {"atual": v, "anterior": v}  # Repete o valor
        
        return {"erro": False, "dados": resultado}
    
    except Exception as e:
        print(f"[BP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''

if padrao.search(c):
    c = padrao.sub(nova_api, c, count=1)
else:
    idx = c.find('@app.get("/analise_bp")')
    if idx == -1: idx = c.find("if __name__")
    if idx == -1: idx = len(c)
    c = c[:idx] + nova_api + c[idx:]

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] API do BP reescrita para buscar os valores corretamente.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_final_{ts}", back_path)
