import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_total_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga do BP (se existir)
padrao = re.compile(r'@app\.get\("/api/analise_bp/\{periodo\}"\).*?(?=@app\.get\("/analise_bp"\))', re.DOTALL)
c = padrao.sub('', c)

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
                if len(p) > 1 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1])
                if len(p) > 3 and termo_norm in remover_acentos(str(p[2])):
                    return limpar(p[3])
            return 0.0
        
        # Busca os valores do Ativo (coluna 0 -> 1) e Passivo (coluna 2 -> 3)
        ativo_circ = buscar("ATIVO CIRCULANTE")
        caixa = buscar("CAIXA E EQUIVALENTES")
        creditos = buscar("CREDITOS A CURTO PRAZO")
        ativo_nao_circ = buscar("ATIVO NAO CIRCULANTE")
        imobilizado = buscar("IMOBILIZADO")
        passivo_circ = buscar("PASSIVO CIRCULANTE")
        passivo_nao_circ = buscar("PASSIVO NAO-CIRCULANTE")
        patrimonio_liq = buscar("RESULTADOS ACUMULADOS")
        
        # Total do Ativo = Ativo Circulante + Ativo Nao Circulante
        total_ativo = ativo_circ + ativo_nao_circ
        
        # Total do Passivo = Passivo Circulante + Passivo Nao Circulante
        total_passivo = passivo_circ + passivo_nao_circ
        
        # Como o CSV so tem o exercicio atual, anterior = 0
        dados = {
            "ativo_circulante": {"atual": ativo_circ, "anterior": 0.0},
            "caixa": {"atual": caixa, "anterior": 0.0},
            "creditos": {"atual": creditos, "anterior": 0.0},
            "ativo_nao_circulante": {"atual": ativo_nao_circ, "anterior": 0.0},
            "imobilizado": {"atual": imobilizado, "anterior": 0.0},
            "total_ativo": {"atual": total_ativo, "anterior": 0.0},
            "passivo_circulante": {"atual": passivo_circ, "anterior": 0.0},
            "passivo_nao_circulante": {"atual": passivo_nao_circ, "anterior": 0.0},
            "total_passivo": {"atual": total_passivo, "anterior": 0.0},
            "patrimonio_liquido": {"atual": patrimonio_liq, "anterior": 0.0},
        }
        
        return {"erro": False, "dados": dados}
    
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
    print("[OK] API do BP atualizada com Total do Ativo e Total do Passivo.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_total_{ts}", back_path)
