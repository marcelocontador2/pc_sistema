"""
Rota do DVP (Análise Patrimonial) — reescrita do zero em 31/10/2026.
"""
import csv
import os
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/api/analise_patrimonial", tags=["analise_patrimonial"])
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
def processar_dvp(caminho):
    dados = {
        "total_vpa": {"atual": 0.0, "anterior": 0.0},
        "vpa_financeiras": {"atual": 0.0, "anterior": 0.0},
        "transf_recebidas": {"atual": 0.0, "anterior": 0.0},
        "outras_vpa": {"atual": 0.0, "anterior": 0.0},
        "reversao_provisoes": {"atual": 0.0, "anterior": 0.0},
        "total_vpd": {"atual": 0.0, "anterior": 0.0},
        "vpd_financeiras": {"atual": 0.0, "anterior": 0.0},
        "pessoal_encargos": {"atual": 0.0, "anterior": 0.0},
        "uso_material_consumo": {"atual": 0.0, "anterior": 0.0},
        "servicos": {"atual": 0.0, "anterior": 0.0},
        "depreciacao": {"atual": 0.0, "anterior": 0.0},
        "amortizacao": {"atual": 0.0, "anterior": 0.0},
        "transf_concedidas": {"atual": 0.0, "anterior": 0.0},
        "outras_vpd": {"atual": 0.0, "anterior": 0.0},
        "tributarias": {"atual": 0.0, "anterior": 0.0},
        "resultado": {"atual": 0.0, "anterior": 0.0},
        "tipo_resultado": {"atual": "", "anterior": ""},
        "margem_resultado": {"atual": 0.0, "anterior": 0.0},
    }
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for row in leitor:
            if len(row) < 8:
                continue
            col_a = row[0].strip().upper()
            col_d = row[4].strip().upper()
            v_aum = limpar(row[2])
            va_aum = limpar(row[3])
            v_dim = limpar(row[6])
            va_dim = limpar(row[7])
            # TOTAIS
            if "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in col_a:
                dados["total_vpa"]["atual"] = v_aum
                dados["total_vpa"]["anterior"] = va_aum
            if "VARIAÇÃO PATRIMONIAL DIMINUTIVA" in col_d:
                dados["total_vpd"]["atual"] = v_dim
                dados["total_vpd"]["anterior"] = va_dim
            # VPA FINANCEIRAS
            if "VARIAÇÕES PATRIMONIAIS AUMENTATIVAS FINANCEIRAS" in col_a:
                dados["vpa_financeiras"]["atual"] = v_aum
                dados["vpa_financeiras"]["anterior"] = va_aum
            # TRANSFERENCIAS RECEBIDAS
            if "TRANSFERÊNCIAS E DELEGAÇÕES RECEBIDAS" in col_a:
                dados["transf_recebidas"]["atual"] = v_aum
                dados["transf_recebidas"]["anterior"] = va_aum
            # OUTRAS VPA
            if "OUTRAS VARIAÇÕES PATRIMONIAIS AUMENTATIVAS" in col_a:
                dados["outras_vpa"]["atual"] = v_aum
                dados["outras_vpa"]["anterior"] = va_aum
            # REVERSAO DE PROVISOES
            if "REVERSÃO DE PROVISÕES E AJUSTES DE PERDAS" in col_a:
                dados["reversao_provisoes"]["atual"] = v_aum
                dados["reversao_provisoes"]["anterior"] = va_aum
            # VPD FINANCEIRAS
            if "VARIAÇÕES PATRIMONIAIS DIMINUTIVAS FINANCEIRAS" in col_d:
                dados["vpd_financeiras"]["atual"] = v_dim
                dados["vpd_financeiras"]["anterior"] = va_dim
            # PESSOAL E ENCARGOS
            if "PESSOAL E ENCARGOS" in col_d:
                dados["pessoal_encargos"]["atual"] = v_dim
                dados["pessoal_encargos"]["anterior"] = va_dim
            # USO DE MATERIAL DE CONSUMO
            if "USO DE MATERIAL DE CONSUMO" in col_d or "CONSUMO DE MATERIAL" in col_d:
                dados["uso_material_consumo"]["atual"] = v_dim
                dados["uso_material_consumo"]["anterior"] = va_dim
            # SERVICOS (linha 21)
            if col_d.strip() == "SERVIÇOS" or col_d.strip() == "SERVICOS":
                dados["servicos"]["atual"] = v_dim
                dados["servicos"]["anterior"] = va_dim
            # DEPRECIACAO (linha 27)
            if "DEPRECIAÇÃO" in col_d and "AMORTIZAÇÃO" not in col_d:
                dados["depreciacao"]["atual"] = v_dim
                dados["depreciacao"]["anterior"] = va_dim
            # AMORTIZACAO (linha 28)
            if "AMORTIZAÇÃO" in col_d and "DEPRECIAÇÃO" not in col_d:
                dados["amortizacao"]["atual"] = v_dim
                dados["amortizacao"]["anterior"] = va_dim
            # TRANSFERENCIAS CONCEDIDAS (linha 32)
            if "TRANSFERÊNCIAS E DELEGAÇÕES CONCEDIDAS" in col_d:
                dados["transf_concedidas"]["atual"] = v_dim
                dados["transf_concedidas"]["anterior"] = va_dim
            # OUTRAS VPD (linha 44)
            if "OUTRAS VARIAÇÕES PATRIMONIAIS DIMINUTIVAS" in col_d and "FINANCEIRAS" not in col_d:
                dados["outras_vpd"]["atual"] = v_dim
                dados["outras_vpd"]["anterior"] = va_dim
            # TRIBUTARIAS
            if "TRIBUTÁRIAS" in col_d or "TRIBUTARIAS" in col_d:
                dados["tributarias"]["atual"] = v_dim
                dados["tributarias"]["anterior"] = va_dim
    # RESULTADO = TOTAL VPA - TOTAL VPD
    dados["resultado"]["atual"] = dados["total_vpa"]["atual"] - dados["total_vpd"]["atual"]
    dados["resultado"]["anterior"] = dados["total_vpa"]["anterior"] - dados["total_vpd"]["anterior"]
    dados["tipo_resultado"]["atual"] = "Superávit Patrimonial" if dados["resultado"]["atual"] >= 0 else "Déficit Patrimonial"
    dados["tipo_resultado"]["anterior"] = "Superávit Patrimonial" if dados["resultado"]["anterior"] >= 0 else "Déficit Patrimonial"
    if dados["total_vpa"]["atual"] > 0:
        dados["margem_resultado"]["atual"] = round((dados["resultado"]["atual"] / dados["total_vpa"]["atual"]) * 100, 2)
    if dados["total_vpa"]["anterior"] > 0:
        dados["margem_resultado"]["anterior"] = round((dados["resultado"]["anterior"] / dados["total_vpa"]["anterior"]) * 100, 2)
    return {"dados": dados}
@router.get("/{periodo}")
async def api_analise_patrimonial(periodo: str):
    p_limpo = periodo.replace("-", "_")
    caminho = os.path.join(UPLOADS_DIR, f"DVP_{p_limpo}.csv")
    if not os.path.exists(caminho):
        return {"erro": "faltando", "pecas": ["DVP"]}
    try:
        return processar_dvp(caminho)
    except Exception as e:
        print(f"[DVP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))
