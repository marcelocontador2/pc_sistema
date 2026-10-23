
import os
import re
import csv
from fastapi import APIRouter, HTTPException

router = APIRouter()

def _get_csv(tipo, periodo):
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    p_limpo = re.sub(r'[^A-Z0-9]', '_', str(periodo).upper()).strip('_')
    nome = f"{tipo}_{p_limpo}.csv"
    caminho = os.path.join(pasta, nome)
    return caminho if os.path.exists(caminho) else None

def _ler_linhas(caminho):
    if not caminho: return []
    with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
        return [ [col.strip().replace('"', '') for col in row] for row in csv.reader(f, delimiter=';') if row ]

def _limpar_valor(valor):
    if not valor: return 0.0
    v = str(valor).upper().replace("R$", "").replace(" ", "").replace("
", "").replace("", "").strip()
    if not v or v == '-': return 0.0
    mult = -1.0 if v.endswith('C') else 1.0
    v = v.replace("C", "").replace("D", "")
    if ',' in v and '.' in v: v = v.replace(".", "").replace(",", ".")
    elif ',' in v: v = v.replace(",", ".")
    try: return float(v) * mult
    except: return 0.0

@router.get("/gerar_matriz/{periodo}")
async def gerar_matriz(periodo: str):
    try:
        # 1. VALIDAÇÃO: Verifica se todos os arquivos obrigatórios existem
        pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
        pecas_faltando = []
        
        for peca in pecas_obrigatorias:
            if not _get_csv(peca, periodo):
                pecas_faltando.append(peca)
                
        if pecas_faltando:
            return {"erro": "faltando", "pecas": pecas_faltando}

        # 2. Se passou, lê os arquivos
        l_bal = _ler_linhas(_get_csv("BALANCETE", periodo))
        l_bp  = _ler_linhas(_get_csv("BALANCO_PATRIMONIAL", periodo))
        l_bf  = _ler_linhas(_get_csv("BALANCO_FINANCEIRO", periodo))
        l_bo  = _ler_linhas(_get_csv("BALANCO_ORCAMENTARIO", periodo))
        l_dfc = _ler_linhas(_get_csv("DFC", periodo))
        l_dvp = _ler_linhas(_get_csv("DVP", periodo))
        l_dmpl= _ler_linhas(_get_csv("DMPL", periodo))

        matriz = []

        def add_linha(nome, bal=0, bp=0, bf=0, bo=0, dfc=0, dvp=0, dmpl=0):
            valores = [v for v in [bal, bp, bf, bo, dfc, dvp, dmpl] if abs(v) > 0.001]
            if len(valores) >= 2:
                conf = "OK" if all(abs(v - valores[0]) < 0.05 for v in valores) else "ERRO"
            elif len(valores) == 1:
                conf = "N/A"
            else:
                conf = "VAZIO"

            def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if v != 0 else "-"

            matriz.append({
                "item": nome, "balancete": fmt(bal), "bp": fmt(bp), "bf": fmt(bf),
                "bo": fmt(bo), "dfc": fmt(dfc), "dvp": fmt(dvp), "dmpl": fmt(dmpl), "conf": conf
            })

        # Lógica do teste (Ativo)
        def _get_val_bal(linhas, termo):
            for p in linhas:
                if len(p) > 4 and termo in p[0].upper(): return _limpar_valor(p[4])
            return 0.0
        def _get_val_bp(linhas, termo, is_passivo=False):
            for p in linhas:
                if len(p) >= 4:
                    txt = p[2].upper() if is_passivo else p[0].upper()
                    if termo in txt: return _limpar_valor(p[3] if is_passivo else p[1])
            return 0.0

        add_linha("ATIVO", _get_val_bal(l_bal, "1 - ATIVO"), _get_val_bp(l_bp, "TOTAL"))
        add_linha("ATIVO CIRCULANTE", _get_val_bal(l_bal, "1.1 - ATIVO CIRCULANTE"), _get_val_bp(l_bp, "ATIVO CIRCULANTE"))
        
        return {"matriz": matriz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
