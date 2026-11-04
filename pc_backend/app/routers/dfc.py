"""
Rota da DFC - Leitura por Blocos (Operacional, Investimento, Financiamento).
"""
import csv
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/analise_dfc", tags=["dfc"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")

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

def processar_dfc(caminho):
    linhas = []
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for row in leitor:
            linhas.append(row)

    # Funcao para achar o indice de um termo na coluna 0 ou 3
    def achar_idx(termo, inicio=0):
        termo = termo.upper().strip()
        for i in range(inicio, len(linhas)):
            p = linhas[i]
            if len(p) > 0 and termo in str(p[0]).upper():
                return i
            if len(p) > 3 and termo in str(p[3]).upper():
                return i
        return -1

    def val(p, idx):
        if p and len(p) > idx:
            return limpar(p[idx])
        return 0.0

    # --- ENCONTRA OS MARCOS (BLOCOS) ---
    idx_oper = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERA")
    idx_invest = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO")
    idx_financ = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO")
    idx_apuracao = achar_idx("APURA")

    if idx_oper == -1 or idx_invest == -1 or idx_financ == -1 or idx_apuracao == -1:
        return {"erro": "estrutura", "mensagem": "Nao foi possivel localizar os blocos da DFC no CSV."}

    # --- BLOCO OPERACIONAL ---
    linhas_oper = linhas[idx_oper:idx_invest]
    def buscar_no_bloco(bloco, termo):
        termo = termo.upper().strip()
        for p in bloco:
            if len(p) > 0 and termo in str(p[0]).upper():
                return p
            if len(p) > 3 and termo in str(p[3]).upper():
                return p
        return None

    l_ing_oper = buscar_no_bloco(linhas_oper, "INGRESSOS")
    l_desemb_oper = buscar_no_bloco(linhas_oper, "DESEMBOLSOS")
    l_liq_oper = buscar_no_bloco(linhas_oper, "FLUXO DE CAIXA L")

    # --- BLOCO INVESTIMENTO ---
    linhas_invest = linhas[idx_invest:idx_financ]
    l_ing_invest = buscar_no_bloco(linhas_invest, "INGRESSOS")
    l_desemb_invest = buscar_no_bloco(linhas_invest, "DESEMBOLSOS")
    l_liq_invest = buscar_no_bloco(linhas_invest, "FLUXO DE CAIXA L")

    # --- BLOCO FINANCIAMENTO ---
    linhas_financ = linhas[idx_financ:idx_apuracao]
    l_ing_financ = buscar_no_bloco(linhas_financ, "INGRESSOS")
    l_desemb_financ = buscar_no_bloco(linhas_financ, "DESEMBOLSOS")
    l_liq_financ = buscar_no_bloco(linhas_financ, "FLUXO DE CAIXA L")

    # --- APURACAO ---
    linhas_apuracao = linhas[idx_apuracao:]
    l_geracao = buscar_no_bloco(linhas_apuracao, "GERA")
    l_caixa_inicial = buscar_no_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA INICIAL")
    l_caixa_final = buscar_no_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA FINAL")

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

@router.get("/{periodo}")
async def api_analise_dfc(periodo: str):
    p_limpo = periodo.replace("-", "_")
    caminho = os.path.join(UPLOADS_DIR, f"DFC_{p_limpo}.csv")
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["DFC"]}
    try:
        return processar_dfc(caminho)
    except Exception as e:
        print(f"[DFC] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))
