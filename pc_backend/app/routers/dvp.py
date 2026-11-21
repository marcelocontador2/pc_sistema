# -*- coding: utf-8 -*-
"""
Rota do DVP (Análise Patrimonial) - PostgreSQL-first.
"""
import csv
import json
import os
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
import psycopg2
from pc_backend.app.config import PG_CONFIG
from pc_backend.app.services.pdf_dvp import desenhar_tabela_dvp, fmt_brl
from pc_backend.core.pdf_utils import novo_pdf, fmt_brl as core_fmt_brl, NOVA_LINHA

router = APIRouter(prefix="/api/analise_patrimonial", tags=["analise_patrimonial"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")


def _schema_dvp_vazio():
    return {
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


def _recalcular_indicadores(dados: dict) -> dict:
    base = _schema_dvp_vazio()
    for k, v in (dados or {}).items():
        base[k] = v

    vpa_atual = float((base.get("total_vpa") or {}).get("atual") or 0.0)
    vpd_atual = float((base.get("total_vpd") or {}).get("atual") or 0.0)
    res_atual = vpa_atual - vpd_atual

    vpa_ant = float((base.get("total_vpa") or {}).get("anterior") or 0.0)
    vpd_ant = float((base.get("total_vpd") or {}).get("anterior") or 0.0)
    res_ant = (vpa_ant - vpd_ant) if (vpa_ant != 0.0 or vpd_ant != 0.0) else float((base.get("resultado") or {}).get("anterior") or 0.0)

    def _classificar(val):
        if val > 0:
            return "Superávit Patrimonial"
        if val < 0:
            return "Déficit Patrimonial"
        return "Nulo"

    tipo_ant = (base.get("tipo_resultado") or {}).get("anterior") or (_classificar(res_ant) if (vpa_ant != 0.0 or vpd_ant != 0.0) else "")
    margem_ant = float((base.get("margem_resultado") or {}).get("anterior") or 0.0)
    if vpa_ant > 0 and margem_ant == 0.0:
        margem_ant = round((res_ant / vpa_ant) * 100, 2)

    base["resultado"] = {"atual": res_atual, "anterior": res_ant}
    base["tipo_resultado"] = {"atual": _classificar(res_atual), "anterior": tipo_ant}
    base["margem_resultado"] = {
        "atual": round((res_atual / vpa_atual) * 100, 2) if vpa_atual > 0 else 0.0,
        "anterior": margem_ant,
    }
    return base


def buscar_dvp_postgresql(periodo: str | None = None, entidade_id: int | None = None):
    """
    Busca dados do DVP diretamente no PostgreSQL (historico_analise_dvp / demonstracao_resumo).
    """
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        row = None
        if periodo:
            sql_periodo = """
                SELECT periodo, resultado_json
                FROM historico_analise_dvp
                WHERE periodo ILIKE %s
            """
            params_periodo = [f"%{periodo}%"]
            if entidade_id is not None:
                sql_periodo += " AND (entidade_id = %s OR entidade_id IS NULL)"
                params_periodo.append(entidade_id)
            sql_periodo += " ORDER BY id DESC LIMIT 1"
            cur.execute(sql_periodo, tuple(params_periodo))
            row = cur.fetchone()

        if not row:
            cur.execute(
                """
                SELECT periodo, resultado_json
                FROM historico_analise_dvp
                ORDER BY id DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()

        if row and row[1]:
            raw = row[1] if isinstance(row[1], dict) else json.loads(row[1])
            dados = _recalcular_indicadores(raw)
            return {"erro": False, "fonte": "postgresql:historico_analise_dvp", "periodo": row[0], "dados": dados}

        # Fallback dentro do PostgreSQL via demonstracao_resumo
        cur.execute(
            """
            SELECT grupo_demonstrativo, valor_atual
            FROM demonstracao_resumo
            WHERE grupo_demonstrativo ILIKE ANY (ARRAY['%VPA%', '%VPD%', '%Superávit%'])
            ORDER BY id DESC
            """
        )
        grupos = cur.fetchall()
        if grupos:
            dados = _schema_dvp_vazio()
            for grupo, val in grupos:
                g_up = str(grupo or "").upper()
                v = float(val or 0.0)
                if "VARIACOES ATIVAS" in g_up or "TOTAL VPA" in g_up:
                    if dados["total_vpa"]["atual"] == 0.0:
                        dados["total_vpa"]["atual"] = v
                    elif dados["total_vpa"]["anterior"] == 0.0:
                        dados["total_vpa"]["anterior"] = v
                elif "VARIACOES DIMINUTIVAS" in g_up or "TOTAL VPD" in g_up:
                    if dados["total_vpd"]["atual"] == 0.0:
                        dados["total_vpd"]["atual"] = v
                    elif dados["total_vpd"]["anterior"] == 0.0:
                        dados["total_vpd"]["anterior"] = v
            if dados["total_vpa"]["atual"] != 0.0 or dados["total_vpd"]["atual"] != 0.0:
                return {
                    "erro": False,
                    "fonte": "postgresql:demonstracao_resumo",
                    "periodo": periodo or "Atual",
                    "dados": _recalcular_indicadores(dados),
                }

        return None
    finally:
        conn.close()


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


def processar_dvp(caminho=None):
    """
    Prioriza PostgreSQL; l? CSV apenas como fallback se caminho existir e o banco n?o tiver dados.
    """
    res_pg = buscar_dvp_postgresql()
    if res_pg:
        return res_pg

    if not caminho or not os.path.exists(caminho):
        return {"erro": "faltando", "mensagem": "Dados do DVP n?o encontrados no PostgreSQL nem em arquivo CSV."}

    dados = _schema_dvp_vazio()
    try:
        with open(caminho, "r", encoding="latin-1") as f:
            linhas = f.readlines()

        for linha in linhas:
            partes = linha.strip().split(";")
            if len(partes) < 7:
                continue

            col_a = partes[0].strip().upper() if len(partes) > 0 else ""
            val_a = limpar(partes[2]) if len(partes) > 2 else 0.0
            val_a_ant = limpar(partes[3]) if len(partes) > 3 else 0.0

            col_d = partes[4].strip().upper() if len(partes) > 4 else ""
            val_d = limpar(partes[6]) if len(partes) > 6 else 0.0
            val_d_ant = limpar(partes[7]) if len(partes) > 7 else 0.0

            if "VARIA??O PATRIMONIAL AUMENTATIVA" in col_a:
                dados["total_vpa"] = {"atual": val_a, "anterior": val_a_ant}
            elif "FINANCEIRAS" in col_a:
                dados["vpa_financeiras"] = {"atual": val_a, "anterior": val_a_ant}
            elif "TRANSFER?NCIAS" in col_a or "TRANSFERENCIAS" in col_a:
                dados["transf_recebidas"] = {"atual": val_a, "anterior": val_a_ant}
            elif "OUTRAS VARIA??ES" in col_a:
                dados["outras_vpa"] = {"atual": val_a, "anterior": val_a_ant}

            if "VARIA??O PATRIMONIAL DIMINUTIVA" in col_d:
                dados["total_vpd"] = {"atual": val_d, "anterior": val_d_ant}
            elif "PESSOAL E ENCARGOS" in col_d:
                dados["pessoal_encargos"] = {"atual": val_d, "anterior": val_d_ant}
            elif "SERVI?OS" in col_d or "SERVICOS" in col_d:
                dados["servicos"] = {"atual": val_d, "anterior": val_d_ant}
            elif "DEPRECIA??O" in col_d or "DEPRECIACAO" in col_d:
                dados["depreciacao"] = {"atual": val_d, "anterior": val_d_ant}
            elif "TRANSFER?NCIAS" in col_d or "TRANSFERENCIAS" in col_d:
                dados["transf_concedidas"] = {"atual": val_d, "anterior": val_d_ant}
            elif "OUTRAS VARIA??ES" in col_d:
                dados["outras_vpd"] = {"atual": val_d, "anterior": val_d_ant}

        return {"fonte": "csv_fallback", "dados": _recalcular_indicadores(dados)}
    except Exception as e:
        print("[DVP] Erro ao processar CSV:", e)
        return {"erro": str(e)}


@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_dvp(periodo: str, periodo_anterior: str, request: Request = None):
    try:
        res_pg = buscar_dvp_postgresql(periodo, resolver_entidade_id(request))
        if not res_pg:
            return {"ok": False, "mensagem": f"Dados do DVP n?o encontrados no PostgreSQL para {periodo}"}

        if not res_pg or res_pg.get("erro"):
            return {"ok": False, "mensagem": (res_pg or {}).get("mensagem", "Dados do DVP n?o encontrados no PostgreSQL")}

        ent_id = resolver_entidade_id(request)
        dados_json = res_pg["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO historico_analise_dvp (periodo, data_geracao, resultado_json, entidade_id)
            VALUES (%s, NOW(), %s, %s) RETURNING id
            """,
            (periodo_label, json.dumps(dados_json, ensure_ascii=False), ent_id),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()

        return {"ok": True, "id": new_id, "fonte": res_pg.get("fonte", "postgresql"), "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[DVP] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico")
def get_historico_dvp(request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        ent_id = resolver_entidade_id(request, conn=conn)
        if ent_id is not None:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dvp WHERE entidade_id = %s ORDER BY id DESC", (ent_id,))
        else:
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
@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_dvp(id: int):
    """Gera PDF do DVP com acentos corretos (usa novo_pdf)."""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "SELECT periodo, resultado_json FROM historico_analise_dvp WHERE id = %s",
            (id,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return Response(content="Registro nao encontrado", media_type="text/plain", status_code=404)

        periodo_label = row[0]
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])

        pdf = novo_pdf(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        W = pdf.w

        pdf.set_fill_color(0, 51, 102)
        pdf.rect(0, 0, W, 30, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 16)
        pdf.set_xy(15, 8)
        pdf.cell(0, 8, "DVP - Demonstração das Variações Patrimoniais")
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(15, 18)
        pdf.cell(0, 6, f"Período: {periodo_label}")

        vpa = (dados.get("total_vpa") or {}).get("atual", 0)
        vpd = (dados.get("total_vpd") or {}).get("atual", 0)
        res = (dados.get("resultado") or {}).get("atual", 0)

        pdf.set_fill_color(227, 242, 253)
        pdf.rect(15, 40, 85, 15, style="F")
        pdf.set_text_color(0, 51, 102)
        pdf.set_font("Arial", "B", 12)
        pdf.set_xy(20, 43)
        pdf.cell(0, 6, fmt_brl(vpa))
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(102, 102, 102)
        pdf.set_xy(20, 50)
        pdf.cell(0, 4, "Total VPA (Varia??es Aumentativas)")

        pdf.set_fill_color(255, 235, 238)
        pdf.rect(110, 40, 85, 15, style="F")
        pdf.set_text_color(220, 53, 69)
        pdf.set_font("Arial", "B", 12)
        pdf.set_xy(115, 43)
        pdf.cell(0, 6, fmt_brl(vpd))
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(102, 102, 102)
        pdf.set_xy(115, 50)
        pdf.cell(0, 4, "Total VPD (Varia??es Diminutivas)")

        pdf.set_fill_color(232, 245, 233)
        pdf.rect(15, 62, 180, 18, style="F")
        pdf.set_text_color(0, 51, 102)
        pdf.set_font("Arial", "B", 14)
        pdf.set_xy(20, 66)
        pdf.cell(0, 7, fmt_brl(res))
        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(20, 73)
        pdf.cell(0, 5, "Superávit Patrimonial")

        desenhar_tabela_dvp(pdf, dados, y_inicial=92)

        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=DVP_{id}.pdf"},
        )
    except Exception as e:
        print("[DVP] PDF erro:", e)
        print(traceback.format_exc())
        return Response(content=f"ERRO: {e}", media_type="text/plain", status_code=500)


@router.get("/{periodo}")
async def api_analise_patrimonial(periodo: str, request: Request = None):
    try:
        res_pg = buscar_dvp_postgresql(periodo, resolver_entidade_id(request))
        if res_pg:
            return res_pg

        # 100% PostgreSQL: sem fallback em arquivo CSV

        return {"erro": "faltando", "pecas": ["DVP"]}
    except Exception as e:
        print(f"[DVP] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))