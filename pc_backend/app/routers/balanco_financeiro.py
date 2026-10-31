"""
Rota do Balanco Financeiro — reescrita em 31/10/2026 com base nas coordenadas do CSV.
"""
import csv
import os
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/api/analise_financeira_bf", tags=["balanco_financeiro"])
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
def processar_bf(caminho):
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
    # === GRUPOS DE RECEITAS ===
    l_rec_corrente = buscar("RECEITAS CORRENTE")
    l_rec_capital = buscar("RECEITAS DE CAPITAL")
    # Detalhes da Receita Corrente
    l_contribuicoes = buscar("CONTRIBUIÇÕES")
    l_rec_aplic_fin = buscar("RECEITAS DE APLICAÇÃO FINANCEIRAS")
    l_transf_atual = buscar("TRANSFERÊNCIAS DOS CONSELHOS REGIONAIS DE ENFERMAGEM - EXERCÍCIO ATUAL")
    l_transf_ant = buscar("TRANSFERÊNCIAS DOS CONSELHOS REGIONAIS DE ENFERMAGEM- EXERCÍCIOS ANTERIORES")
    l_indenizacoes = buscar("INDENIZAÇÕES, RESTITUIÇÕES E RESSARCIMENTO")
    l_doacoes = buscar("DOAÇÕES")
    # === GRUPOS DE DESPESAS ===
    l_desp_corrente = buscar("CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE")
    l_pessoal = buscar("PESSOAL E ENCARGOS SOCIAIS")
    l_outras_desp_correntes = buscar("OUTRAS DESPESAS CORRENTES")
    l_desp_capital = buscar("CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CAPITAL")
    l_investimentos = buscar("INVESTIMENTOS")
    l_inversoes = buscar("INVERSÕES FINANCEIRAS")
    # === CAIXA ===
    l_saldo_ant = buscar("Saldo em espécie do Exercício Anterior")
    l_saldo_seg = buscar("Saldo em espécie para o Exercício Seguinte")
    l_rec_extra = buscar("Recebimentos Extraorçamentários")
    l_pag_extra = buscar("Pagamentos Extraorçamentários")
    dados = {
        # Receitas
        "receitas": {
            "corrente": {"atual": val(l_rec_corrente, 1), "anterior": val(l_rec_corrente, 2)},
            "capital": {"atual": val(l_rec_capital, 1), "anterior": val(l_rec_capital, 2)},
            "detalhes": {
                "contribuicoes": {"atual": val(l_contribuicoes, 1), "anterior": val(l_contribuicoes, 2)},
                "aplicacoes": {"atual": val(l_rec_aplic_fin, 1), "anterior": val(l_rec_aplic_fin, 2)},
                "transf_atual": {"atual": val(l_transf_atual, 1), "anterior": val(l_transf_atual, 2)},
                "transf_ant": {"atual": val(l_transf_ant, 1), "anterior": val(l_transf_ant, 2)},
                "indenizacoes": {"atual": val(l_indenizacoes, 1), "anterior": val(l_indenizacoes, 2)},
                "doacoes": {"atual": val(l_doacoes, 1), "anterior": val(l_doacoes, 2)},
            }
        },
        # Despesas
        "despesas": {
            "corrente": {"atual": val(l_desp_corrente, 4), "anterior": val(l_desp_corrente, 5)},
            "capital": {"atual": val(l_desp_capital, 4), "anterior": val(l_desp_capital, 5)},
            "detalhes": {
                "pessoal": {"atual": val(l_pessoal, 4), "anterior": val(l_pessoal, 5)},
                "outras_correntes": {"atual": val(l_outras_desp_correntes, 4), "anterior": val(l_outras_desp_correntes, 5)},
                "investimentos": {"atual": val(l_investimentos, 4), "anterior": val(l_investimentos, 5)},
                "inversoes": {"atual": val(l_inversoes, 4), "anterior": val(l_inversoes, 5)},
            }
        },
        # Extraorçamentário
        "extra": {
            "recebimentos": {"atual": val(l_rec_extra, 1), "anterior": val(l_rec_extra, 2)},
            "pagamentos": {"atual": val(l_pag_extra, 4), "anterior": val(l_pag_extra, 5)},
        },
        # Caixa
        "caixa": {
            "saldo_anterior": {"atual": val(l_saldo_ant, 1), "anterior": val(l_saldo_ant, 2)},
            "saldo_seguinte": {"atual": val(l_saldo_seg, 4), "anterior": val(l_saldo_seg, 5)},
        }
    }
    # Calculando os totais
    dados["receitas"]["total"] = {
        "atual": dados["receitas"]["corrente"]["atual"] + dados["receitas"]["capital"]["atual"],
        "anterior": dados["receitas"]["corrente"]["anterior"] + dados["receitas"]["capital"]["anterior"]
    }
    dados["despesas"]["total"] = {
        "atual": dados["despesas"]["corrente"]["atual"] + dados["despesas"]["capital"]["atual"],
        "anterior": dados["despesas"]["corrente"]["anterior"] + dados["despesas"]["capital"]["anterior"]
    }
    # Geração Líquida de Caixa
    geracao_atual = (
        dados["receitas"]["total"]["atual"] + dados["extra"]["recebimentos"]["atual"]
        - dados["despesas"]["total"]["atual"] - dados["extra"]["pagamentos"]["atual"]
    )
    geracao_anterior = (
        dados["receitas"]["total"]["anterior"] + dados["extra"]["recebimentos"]["anterior"]
        - dados["despesas"]["total"]["anterior"] - dados["extra"]["pagamentos"]["anterior"]
    )
    dados["caixa"]["geracao_liquida"] = {"atual": geracao_atual, "anterior": geracao_anterior}
    return {"erro": False, "dados": dados}
@router.get("/{periodo}")
async def api_analise_financeira_bf(periodo: str):
    p_limpo = periodo.replace("-", "_")
    caminho = os.path.join(UPLOADS_DIR, f"BALANCO_FINANCEIRO_{p_limpo}.csv")
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["Balanco Financeiro"]}
    try:
        return processar_bf(caminho)
    except Exception as e:
        print(f"[BF] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))
