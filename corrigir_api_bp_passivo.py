import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_api_bp_passivo_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Remove a API antiga do BP
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
        
        # Ativo: Col0 (esp), Col1 (atual), Col2 (anterior)
        # Passivo: Col3 (esp), Col4 (atual), Col5 (anterior)
        
        def buscar_ativo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 2 and termo_norm in remover_acentos(str(p[0])):
                    return limpar(p[1]), limpar(p[2])
            return 0.0, 0.0
        
        def buscar_passivo(termo):
            termo_norm = remover_acentos(termo)
            for p in linhas:
                if len(p) > 5 and termo_norm in remover_acentos(str(p[3])):
                    return limpar(p[4]), limpar(p[5])
            return 0.0, 0.0
        
        # Busca os valores (atual, anterior)
        ativo_circ_at, ativo_circ_ant = buscar_ativo("ATIVO CIRCULANTE")
        caixa_at, caixa_ant = buscar_ativo("CAIXA E EQUIVALENTES")
        creditos_at, creditos_ant = buscar_ativo("CRÉDITOS A CURTO PRAZO")
        ativo_nao_circ_at, ativo_nao_circ_ant = buscar_ativo("ATIVO NÃO CIRCULANTE")
        ativo_realizavel_at, ativo_realizavel_ant = buscar_ativo("ATIVO REALIZÁVEL A LONGO PRAZO")
        imobilizado_at, imobilizado_ant = buscar_ativo("IMOBILIZADO")
        
        passivo_circ_at, passivo_circ_ant = buscar_passivo("PASSIVO CIRCULANTE")
        passivo_nao_circ_at, passivo_nao_circ_ant = buscar_passivo("PASSIVO NAO-CIRCULANTE")
        pl_at, pl_ant = buscar_passivo("RESULTADOS ACUMULADOS")
        
        # Total do Ativo
        total_ativo_at = ativo_circ_at + ativo_nao_circ_at
        total_ativo_ant = ativo_circ_ant + ativo_nao_circ_ant
        
        # PASSIVO TOTAL = Passivo Circulante + Passivo Nao Circulante
        passivo_total_at = passivo_circ_at + passivo_nao_circ_at
        passivo_total_ant = passivo_circ_ant + passivo_nao_circ_ant
        
        # TOTAL DO PASSIVO = Passivo Total + Patrimonio Liquido
        total_passivo_at = passivo_total_at + pl_at
        total_passivo_ant = passivo_total_ant + pl_ant
        
        dados = {
            "ativo_circulante": {"atual": ativo_circ_at, "anterior": ativo_circ_ant},
            "caixa": {"atual": caixa_at, "anterior": caixa_ant},
            "creditos": {"atual": creditos_at, "anterior": creditos_ant},
            "ativo_nao_circulante": {"atual": ativo_nao_circ_at, "anterior": ativo_nao_circ_ant},
            "ativo_realizavel": {"atual": ativo_realizavel_at, "anterior": ativo_realizavel_ant},
            "imobilizado": {"atual": imobilizado_at, "anterior": imobilizado_ant},
            "total_ativo": {"atual": total_ativo_at, "anterior": total_ativo_ant},
            "passivo_circulante": {"atual": passivo_circ_at, "anterior": passivo_circ_ant},
            "passivo_nao_circulante": {"atual": passivo_nao_circ_at, "anterior": passivo_nao_circ_ant},
            "passivo_total": {"atual": passivo_total_at, "anterior": passivo_total_ant},
            "patrimonio_liquido": {"atual": pl_at, "anterior": pl_ant},
            "total_passivo": {"atual": total_passivo_at, "anterior": total_passivo_ant},
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
    print("[OK] API da Analise BP corrigida: 'Passivo Total' e 'Total do Passivo' (com PL).")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_api_bp_passivo_{ts}", back_path)
