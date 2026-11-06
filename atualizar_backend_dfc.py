import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "pc_backend/app/routers/dfc.py"
shutil.copy2(back_path, f"{back_path}.bak_estrutura_{ts}")

novo_conteudo = '''"""
Rota da Demonstração do Fluxo de Caixa (DFC) — adaptada para o CSV do COFEN.
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

    def buscar(termo):
        termo = termo.upper().strip()
        for p in linhas:
            if len(p) > 0 and termo in str(p[0]).upper():
                return p
            if len(p) > 3 and termo in str(p[3]).upper():
                return p
        return None

    def val(p, idx):
        if p and len(p) > idx:
            return abs(limpar(p[idx]))
        return 0.0

    # Operacional
    l_ing_oper = buscar("INGRESSOS") # O primeiro INGRESSOS é o operacional
    l_desemb_oper = buscar("DESEMBOLSOS") # O primeiro DESEMBOLSOS é o operacional
    l_liq_oper = buscar("FLUXO DE CAIXA LÍQUIDO DAS ATIVIDADES DAS OPERAÇŐES")
    
    # Investimento
    # Como tem vários "INGRESSOS", precisamos pegar o segundo
    linhas_ingressos = [p for p in linhas if "INGRESSOS" in str(p[0]).upper() or "INGRESSOS" in str(p[3]).upper()]
    l_ing_invest = linhas_ingressos[1] if len(linhas_ingressos) > 1 else None
    
    linhas_desembolsos = [p for p in linhas if "DESEMBOLSOS" in str(p[0]).upper() or "DESEMBOLSOS" in str(p[3]).upper()]
    l_desemb_invest = linhas_desembolsos[1] if len(linhas_desembolsos) > 1 else None
    l_liq_invest = buscar("FLUXO DE CAIXA LÍQUIDO DAS ATIVIDADES DE INVESTIMENTO")

    # Financiamento
    l_ing_financ = linhas_ingressos[2] if len(linhas_ingressos) > 2 else None
    l_desemb_financ = linhas_desembolsos[2] if len(linhas_desembolsos) > 2 else None
    l_liq_financ = buscar("FLUXO DE CAIXA LÍQUIDO DAS ATIVIDADES DE FINANCIAMENTO")

    # Caixa
    l_geracao = buscar("GERAÇĂO LIQUIDA DE CAIXA E EQUIVALENTES DE CAIXA")
    l_caixa_inicial = buscar("CAIXA E EQUIVALENTES DE CAIXA INICIAL")
    l_caixa_final = buscar("CAIXA E EQUIVALENTES DE CAIXA FINAL")

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
'''
with open(back_path, "w", encoding="utf-8") as f:
    f.write(novo_conteudo)
print("[OK] Backend dfc.py atualizado com a leitura correta.")
