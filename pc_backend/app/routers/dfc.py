# -*- coding: utf-8 -*-
"""
Rota da DFC - PostgreSQL-first (com fallback opcional para CSV).
"""
import csv
import json
import os
import time
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
from fastapi.responses import FileResponse
import psycopg2
from pc_backend.app.config import PG_CONFIG

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


def buscar_dfc_postgresql(periodo: str | None = None, entidade_id: int | None = None):
    """
    Busca dados da DFC diretamente no PostgreSQL (historico_analise_dfc).
    """
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        row = None
        if periodo:
            cur.execute(
                """
                SELECT periodo, resultado_json
                FROM historico_analise_dfc
                WHERE periodo ILIKE %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (f"%{periodo}%",),
            )
            row = cur.fetchone()

        if not row:
            cur.execute(
                """
                SELECT periodo, resultado_json
                FROM historico_analise_dfc
                ORDER BY id DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()

        if row and row[1]:
            dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
            return {
                "erro": False,
                "fonte": "postgresql:historico_analise_dfc",
                "periodo": row[0],
                "dados": dados,
            }
        return None
    finally:
        conn.close()


def processar_dfc(caminho=None, periodo: str | None = None):
    res_pg = buscar_dfc_postgresql(periodo, resolver_entidade_id(request))
    if res_pg:
        return res_pg
    return {"erro": "faltando", "mensagem": "Dados da DFC não encontrados no PostgreSQL."}


@router.get("/analise_dfc")
async def serve_analise_dfc():
    caminho = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "pc_frontend",
        "analise_dfc.html",
    )
    if os.path.exists(caminho):
        return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})
    return {"erro": "Arquivo HTML não encontrado", "caminho": caminho}


@router.post("/salvar/{periodo}/{periodo_anterior}")
async def salvar_analise_dfc(periodo: str, periodo_anterior: str, request: Request = None):
    try:
        res_pg = buscar_dfc_postgresql(periodo, resolver_entidade_id(request))
        if not res_pg:
            return {"ok": False, "mensagem": f"Dados da DFC não encontrados no PostgreSQL para {periodo}"}

        if not res_pg or res_pg.get("erro"):
            return {"ok": False, "mensagem": (res_pg or {}).get("mensagem", "Dados da DFC não encontrados no PostgreSQL")}

        dados_json = res_pg["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO historico_analise_dfc (periodo, data_geracao, resultado_json, entidade_id)
            VALUES (%s, NOW(), %s, %s) RETURNING id
            """,
            (periodo_label, json.dumps(dados_json)),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()

        return {"ok": True, "id": new_id, "fonte": res_pg.get("fonte", "postgresql"), "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[DFC] Erro ao salvar: {e}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico")
async def get_historico_dfc(request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        ent_id = resolver_entidade_id(request, conn=conn)
        if ent_id is not None:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dfc WHERE entidade_id = %s ORDER BY id DESC", (ent_id,))
        else:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dfc ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[DFC] Erro ao listar histórico: {e}")
        return []


@router.get("/historico/{id}")
async def get_historico_dfc_id(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dfc WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Não encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.delete("/excluir/{id}")
async def excluir_dfc(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_dfc WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_dfc(id: int, request: Request = None):
    try:
        from playwright.sync_api import sync_playwright

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dfc WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return Response(content="Registro não encontrado".encode("utf-8"), media_type="text/plain", status_code=404)

        url = (str(request.base_url).rstrip("/") if request and "testserver" not in str(request.base_url) else os.getenv("PC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")) + "/api/analise_dfc/analise_dfc?id=" + str(id) + "&_t=" + str(int(time.time()))

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.evaluate("() => { const el = document.querySelector('.top-bar, .filtros, .sidebar, .btn'); if (el) el.style.display = 'none'; }")
            page.add_style_tag(content="button, select, .top-bar, .filtros, .sidebar { display: none !important; }")
            page.wait_for_function("() => { const box = document.getElementById('dfc-grafico-svg'); return box && box.innerHTML.includes('<svg'); }", timeout=8000)
            page.wait_for_timeout(500)
            pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"})
            browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Analise_DFC_{id}.pdf"},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[DFC] ERRO NO PDF: {e}\n{tb}")
        return Response(content=f"ERRO: {e}\n\n{tb}".encode("utf-8"), media_type="text/plain", status_code=500)


@router.get("/{periodo}")
def api_analise_dfc(periodo: str, request: Request = None):
    try:
        res_pg = buscar_dfc_postgresql(periodo, resolver_entidade_id(request))
        if res_pg:
            return res_pg

        return {"erro": "faltando", "mensagem": f"Dados da DFC não encontrados no PostgreSQL para {periodo}"}
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[DFC] ERRO: {e}\n{tb}")
        return {"erro": "interno", "mensagem": str(e)}