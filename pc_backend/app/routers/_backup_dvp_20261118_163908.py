"""
Rota do DVP (AnÃ¡lise Patrimonial) â€” reescrita do zero em 31/10/2026.
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

    try:
        with open(caminho, "r", encoding="latin-1") as f:
            linhas = f.readlines()

        for linha in linhas:
            partes = linha.strip().split(";")
            if len(partes) < 7:
                continue
            
            # O formato tem: Descricao VPA;;VPA_Atual;VPA_Anterior;Descricao VPD;;VPD_Atual;VPD_Anterior
            # Ou seja, as colunas 2 e 3 são os valores atuais e anteriores do VPA
            # E as colunas 6 e 7 são os valores atuais e anteriores do VPD
            # Mas alguns itens são apenas de um lado.
            
            col_a = partes[0].strip().upper() if len(partes) > 0 else ""
            val_a = limpar(partes[2]) if len(partes) > 2 else 0.0
            val_a_ant = limpar(partes[3]) if len(partes) > 3 else 0.0
            
            col_d = partes[4].strip().upper() if len(partes) > 4 else ""
            val_d = limpar(partes[6]) if len(partes) > 6 else 0.0
            val_d_ant = limpar(partes[7]) if len(partes) > 7 else 0.0

            # --- VPA ---
            if "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in col_a:
                dados["total_vpa"] = {"atual": val_a, "anterior": val_a_ant}
            elif "FINANCEIRAS" in col_a:
                dados["vpa_financeiras"] = {"atual": val_a, "anterior": val_a_ant}
            elif "TRANSFERÊNCIAS" in col_a or "TRANSFERENCIAS" in col_a:
                dados["transf_recebidas"] = {"atual": val_a, "anterior": val_a_ant}
            elif "OUTRAS VARIAÇÕES" in col_a:
                dados["outras_vpa"] = {"atual": val_a, "anterior": val_a_ant}
            
            # --- VPD ---
            if "VARIAÇÃO PATRIMONIAL DIMINUTIVA" in col_d:
                dados["total_vpd"] = {"atual": val_d, "anterior": val_d_ant}
            elif "PESSOAL E ENCARGOS" in col_d:
                dados["pessoal_encargos"] = {"atual": val_d, "anterior": val_d_ant}
            elif "SERVIÇOS" in col_d or "SERVICOS" in col_d:
                dados["servicos"] = {"atual": val_d, "anterior": val_d_ant}
            elif "DEPRECIAÇÃO" in col_d or "DEPRECIACAO" in col_d:
                dados["depreciacao"] = {"atual": val_d, "anterior": val_d_ant}
            elif "TRANSFERÊNCIAS" in col_d or "TRANSFERENCIAS" in col_d:
                dados["transf_concedidas"] = {"atual": val_d, "anterior": val_d_ant}
            elif "OUTRAS VARIAÇÕES" in col_d:
                dados["outras_vpd"] = {"atual": val_d, "anterior": val_d_ant}

        # Calcula o Resultado
        vpa = dados["total_vpa"]["atual"]
        vpd = dados["total_vpd"]["atual"]
        resultado = vpa - vpd
        dados["resultado"] = {"atual": resultado, "anterior": 0.0}
        
        if resultado > 0:
            dados["tipo_resultado"]["atual"] = "Superávit Patrimonial"
        elif resultado < 0:
            dados["tipo_resultado"]["atual"] = "Déficit Patrimonial"
        else:
            dados["tipo_resultado"]["atual"] = "Nulo"
            
        if vpa > 0:
            dados["margem_resultado"]["atual"] = round((resultado / vpa) * 100, 2)

        return {"dados": dados}
    except Exception as e:
        print("[DVP] Erro ao processar CSV:", e)
        return {"erro": str(e)}@router.get("/{periodo}")
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

# ============================================================
# ROTAS DE SALVAR, HISTÃ“RICO E PDF (PostgreSQL)
# ============================================================
import json
from datetime import datetime
from fastapi import Response
import psycopg2
from pc_backend.app.config import PG_CONFIG


@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_dvp(periodo: str, periodo_anterior: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"DVP_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"ok": False, "mensagem": f"CSV nao encontrado: DVP_{p_limpo}.csv"}
        
        resultado = processar_dvp(caminho)
        if resultado.get("erro"):
            return {"ok": False, "mensagem": resultado.get("mensagem", "Erro no processamento")}
        
        dados_json = resultado["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historico_analise_dvp (periodo, data_geracao, resultado_json)
            VALUES (%s, NOW(), %s) RETURNING id
        """, (periodo_label, json.dumps(dados_json, ensure_ascii=False)))
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        import traceback
        print(f"[DVP] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico")
def get_historico_dvp():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dvp ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[DVP] Erro ao listar historico: {e}")
        return []


@router.get("/historico/{id}")
def get_historico_dvp_id(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dvp WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.delete("/excluir/{id}")
def excluir_dvp(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_dvp WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf_novo/{id}")
def gerar_pdf_analise_dvp(id: int):
    from pc_backend.main import gerar_pdf_analise_patrimonial
    return gerar_pdf_analise_patrimonial(id)



