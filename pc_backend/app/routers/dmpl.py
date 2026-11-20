# -*- coding: utf-8 -*-
"""
Rota do DMPL (Demonstra??o das Muta??es do Patrim?nio L?quido) - PostgreSQL-first.
"""
import csv
import json
import os
import time
import traceback
from fastapi import APIRouter, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
import psycopg2
from pc_backend.app.config import PG_CONFIG
from pc_backend.app.db_memoria import salvar_contas_memoria, carregar_contas_memoria, _slug_conta

router = APIRouter(prefix="/api/analise_dmpl", tags=["dmpl"])
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


def _persistir_dmpl_memoria(periodo: str, dados_json: dict) -> None:
    try:
        itens = []
        for idx, m in enumerate(dados_json.get("movimentacoes") or []):
            if isinstance(m, dict):
                desc = str(m.get("especificacao") or m.get("descricao") or f"movimentacao_{idx+1}").strip()
                val = m.get("total")
                if val is None and isinstance(m.get("valores"), dict):
                    val = m["valores"].get("total") or m["valores"].get("TOTAL")
                try:
                    fval = float(val or 0.0)
                except (TypeError, ValueError):
                    fval = 0.0
                itens.append({
                    "chave": f"mov_{_slug_conta(desc)}_{idx+1}",
                    "descricao": desc,
                    "valor": fval,
                    "extra": m,
                })
        res_p = dados_json.get("resultado_periodo") or {}
        if isinstance(res_p, dict):
            for k in ("atual", "anterior"):
                if k in res_p:
                    try:
                        fval = float(res_p.get(k) or 0.0)
                    except (TypeError, ValueError):
                        fval = 0.0
                    itens.append({
                        "chave": f"resultado_periodo_{k}",
                        "descricao": f"Resultado do Per?odo ({k})",
                        "valor": fval,
                        "extra": {"campo": k, "valor": fval},
                    })
        if itens:
            salvar_contas_memoria("DMPL", periodo, itens)
    except Exception as e:
        print(f"[DMPL] Aviso ao salvar memoria PG: {e}")


def _montar_dmpl_da_memoria(periodo: str) -> dict | None:
    mem = carregar_contas_memoria("DMPL", periodo)
    if not mem:
        return None
    movs = []
    res_atual = 0.0
    res_ant = 0.0
    for item in mem:
        chave = item.get("chave", "")
        extra = item.get("dados_json") if isinstance(item.get("dados_json"), dict) else {}
        if chave == "resultado_periodo_atual":
            res_atual = float(item.get("valor") or 0.0)
        elif chave == "resultado_periodo_anterior":
            res_ant = float(item.get("valor") or 0.0)
        else:
            if "especificacao" in extra or "valores" in extra:
                movs.append(extra)
            else:
                movs.append({
                    "especificacao": item.get("descricao"),
                    "total": item.get("valor"),
                    "valores": {"TOTAL": item.get("valor")},
                })
    return {
        "periodo": periodo,
        "fonte": "postgresql_memoria",
        "movimentacoes": movs,
        "resultado_periodo": {"atual": res_atual, "anterior": res_ant},
    }


def buscar_dmpl_postgresql(periodo: str | None = None, entidade_id: int | None = None):
    """
    Busca dados do DMPL diretamente no PostgreSQL (historico_analise_dmpl -> db_memoria).
    """
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        row = None
        if periodo:
            if entidade_id is not None:
                cur.execute(
                    """
                    SELECT periodo, resultado_json
                    FROM historico_analise_dmpl
                    WHERE periodo ILIKE %s AND entidade_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (f"%{periodo}%", entidade_id),
                )
            else:
                cur.execute(
                    """
                    SELECT periodo, resultado_json
                    FROM historico_analise_dmpl
                    WHERE periodo ILIKE %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (f"%{periodo}%",),
                )
            row = cur.fetchone()

        if not row:
            if entidade_id is not None:
                cur.execute(
                    """
                    SELECT periodo, resultado_json
                    FROM historico_analise_dmpl
                    WHERE entidade_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (entidade_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT periodo, resultado_json
                    FROM historico_analise_dmpl
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
            row = cur.fetchone()

        if row and row[1]:
            dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
            return {
                "erro": False,
                "fonte": "postgresql:historico_analise_dmpl",
                "periodo": row[0],
                "dados": dados,
            }
    finally:
        conn.close()

    if periodo:
        mem_dados = _montar_dmpl_da_memoria(periodo)
        if mem_dados is not None:
            return {"erro": False, "fonte": "postgresql_memoria", "periodo": periodo, "dados": mem_dados}

    return None


def processar_dmpl(caminho=None, periodo: str | None = None):
    if periodo:
        conn = psycopg2.connect(**PG_CONFIG)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT resultado_json FROM historico_analise_dmpl WHERE periodo = %s ORDER BY id DESC LIMIT 1",
                (periodo,),
            )
            row = cur.fetchone()
            if row and row[0]:
                rj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                return {"erro": False, "fonte": "postgresql", "dados": rj}
        finally:
            conn.close()
    return {"erro": "faltando", "mensagem": "Dados da DMPL nao encontrados no PostgreSQL."}


@router.get("/historico")
def get_historico_dmpl(request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        ent_id = resolver_entidade_id(request, conn=conn)
        if ent_id is not None:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dmpl WHERE entidade_id = %s ORDER BY id DESC", (ent_id,))
        else:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dmpl ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[DMPL] Erro ao listar historico: {e}")
        return []



@router.get("/{periodo}")
def api_analise_dmpl(periodo: str, request: Request = None):
    try:
        res_pg = buscar_dmpl_postgresql(periodo, resolver_entidade_id(request))
        if res_pg:
            return res_pg

        return {"erro": "faltando", "mensagem": f"Dados do DMPL n?o encontrados no PostgreSQL para: {periodo}"}
    except Exception as e:
        print(f"[DMPL] ERRO: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}



@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_dmpl(periodo: str, periodo_anterior: str, request: Request = None):
    try:
        res_pg = buscar_dmpl_postgresql(periodo)
        if res_pg and isinstance(res_pg.get("dados"), dict):
            dados_json = res_pg["dados"]
            fonte = res_pg.get("fonte", "postgresql")
        else:
            return {"ok": False, "mensagem": f"Dados do DMPL n?o encontrados no PostgreSQL para: {periodo}"}

        periodo_label = f"{periodo} vs {periodo_anterior}"

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        __ent_id_save = resolver_entidade_id(request)
        cur.execute(
            """
            INSERT INTO historico_analise_dmpl (periodo, data_geracao, resultado_json, entidade_id)
            VALUES (%s, NOW(), %s, %s) RETURNING id
            """,
            (periodo_label, json.dumps(dados_json, ensure_ascii=False), __ent_id_save),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()

        return {"ok": True, "id": new_id, "fonte": fonte, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[DMPL] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico/{id}")
def get_historico_dmpl_id(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dmpl WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.delete("/excluir/{id}")
def excluir_dmpl(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_dmpl WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_dmpl(id: int):
    try:
        from playwright.sync_api import sync_playwright

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dmpl WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)

        url = "http://127.0.0.1:994/analise_dmpl?id=" + str(id) + "&_t=" + str(int(time.time()))

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.add_style_tag(content="button, select, .top-bar, .filtros, .sidebar { display: none !important; }")
            page.wait_for_timeout(1000)
            pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"})
            browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Analise_DMPL_{id}.pdf"},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[DMPL] ERRO NO PDF: {e}\n{tb}")
        return Response(content=f"ERRO: {e}\n\n{tb}".encode("utf-8"), media_type="text/plain", status_code=500)