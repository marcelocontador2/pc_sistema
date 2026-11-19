from pc_backend.app.config import PG_CONFIG
import psycopg2
# -*- coding: utf-8 -*-
"""
Rotas de Comparativo de Despesas.
Extraído do main.py para refatoração.
"""
import os
import json
import datetime
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")

router = APIRouter()

from pc_backend.app.db_memoria import salvar_contas_memoria, carregar_contas_memoria, _slug_conta

def _persistir_despesas_memoria(periodo: str, dados: dict) -> None:
    if not periodo or not isinstance(dados, dict):
        return
    itens = [{
        "chave": "despesa_total",
        "descricao": "DESPESA TOTAL",
        "valor": float(dados.get("empenhado_total") or dados.get("liquidado_total") or 0.0),
        "extra": {
            "tipo": "total",
            "orcado": float(dados.get("orcado_total") or 0.0),
            "empenhado": float(dados.get("empenhado_total") or 0.0),
            "liquidado": float(dados.get("liquidado_total") or 0.0),
            "percentual": float(dados.get("percentual_total") or 0.0),
        },
    }]
    for idx, g in enumerate(dados.get("grupos") or []):
        if isinstance(g, dict):
            nome = str(g.get("nome") or f"grupo_{idx+1}").strip()
            val = g.get("empenhado") if g.get("empenhado") is not None else (g.get("liquidado") or 0.0)
            itens.append({
                "chave": f"grupo_{_slug_conta(nome)}",
                "descricao": nome,
                "valor": float(val or 0.0),
                "extra": {
                    "tipo": "grupo",
                    "nome": nome,
                    "orcado": float(g.get("orcado") or 0.0),
                    "empenhado": float(g.get("empenhado") or 0.0),
                    "liquidado": float(g.get("liquidado") or 0.0),
                    "percentual": float(g.get("percentual") or 0.0),
                },
            })
    try:
        salvar_contas_memoria("COMPARATIVO_DESPESAS", periodo, itens)
    except Exception as e:
        print(f"[DESPESAS] Aviso ao salvar memoria PG: {e}")

def _carregar_despesas_memoria(periodo: str) -> dict | None:
    mem = carregar_contas_memoria("COMPARATIVO_DESPESAS", periodo)
    if not mem:
        return None
    dados = {
        "orcado_total": 0.0,
        "empenhado_total": 0.0,
        "liquidado_total": 0.0,
        "percentual_total": 0.0,
        "grupos": [],
    }
    for item in mem:
        extra = item.get("dados_json") if isinstance(item.get("dados_json"), dict) else {}
        tipo = extra.get("tipo")
        if tipo == "total" or item.get("chave") == "despesa_total":
            dados["orcado_total"] = float(extra.get("orcado") or 0.0)
            dados["empenhado_total"] = float(extra.get("empenhado") if extra.get("empenhado") is not None else (item.get("valor") or 0.0))
            dados["liquidado_total"] = float(extra.get("liquidado") if extra.get("liquidado") is not None else (item.get("valor") or 0.0))
            dados["percentual_total"] = float(extra.get("percentual") or 0.0)
        elif tipo == "grupo":
            dados["grupos"].append({
                "nome": extra.get("nome") or item.get("descricao"),
                "orcado": float(extra.get("orcado") or 0.0),
                "empenhado": float(extra.get("empenhado") if extra.get("empenhado") is not None else (item.get("valor") or 0.0)),
                "liquidado": float(extra.get("liquidado") if extra.get("liquidado") is not None else (item.get("valor") or 0.0)),
                "percentual": float(extra.get("percentual") or 0.0),
            })
    return dados


def _buscar_despesas_pg(periodo_str: str) -> dict | None:
    if not periodo_str:
        return None
    mem = _carregar_despesas_memoria(periodo_str)
    if mem and (mem.get("empenhado_total") or mem.get("liquidado_total") or mem.get("orcado_total") or mem.get("grupos")):
        return mem

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT dados_json FROM historico_comparativo_despesas WHERE periodo = %s ORDER BY id DESC LIMIT 1",
            (periodo_str,),
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                "SELECT dados_json FROM historico_comparativo_despesas WHERE periodo ILIKE %s ORDER BY id DESC LIMIT 1",
                (f"%{periodo_str}%",),
            )
            row = cur.fetchone()
        if not row or not row[0]:
            return None
        dj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        if not isinstance(dj, dict):
            return None
        src = dj.get("atual") if isinstance(dj.get("atual"), dict) else dj
        dados = {
            "orcado_total": float(src.get("orcado_total") or 0.0),
            "empenhado_total": float(src.get("empenhado_total") or 0.0),
            "liquidado_total": float(src.get("liquidado_total") or 0.0),
            "percentual_total": float(src.get("percentual_total") or 0.0),
            "grupos": src.get("grupos") or [],
            "detalhes": src.get("detalhes") or [],
            "anterior": dj.get("anterior") if isinstance(dj.get("anterior"), dict) else src.get("anterior"),
        }
        _persistir_despesas_memoria(periodo_str, dados)
        return dados
    except Exception as e:
        print(f"[DESPESAS] Erro ao consultar PostgreSQL ({periodo_str}): {e}")
        return None
    finally:
        conn.close()


def api_comparativo_despesas_v2(periodo: str):
    atual = _buscar_despesas_pg(periodo)
    if not atual:
        return {"erro": True, "mensagem": f"Dados de despesas n?o encontrados no PostgreSQL para o per?odo {periodo}."}

    anterior = atual.get("anterior")
    if not anterior:
        partes = periodo.split("-")
        if len(partes) == 3:
            try:
                periodo_anterior = f"{int(partes[0]) - 1}-{partes[1]}-{partes[2]}"
                anterior = _buscar_despesas_pg(periodo_anterior)
            except Exception:
                anterior = None

    retorno = {
        "orcado_total": atual.get("orcado_total", 0.0),
        "empenhado_total": atual.get("empenhado_total", 0.0),
        "liquidado_total": atual.get("liquidado_total", 0.0),
        "percentual_total": atual.get("percentual_total", 0.0),
        "grupos": atual.get("grupos", []),
        "detalhes": atual.get("detalhes", []),
    }

    if isinstance(anterior, dict):
        retorno["anterior"] = {
            "orcado_total": anterior.get("orcado_total", 0.0),
            "empenhado_total": anterior.get("empenhado_total", 0.0),
            "liquidado_total": anterior.get("liquidado_total", 0.0),
            "percentual_total": anterior.get("percentual_total", 0.0),
            "grupos": anterior.get("grupos", []),
            "detalhes": anterior.get("detalhes", []),
        }
    else:
        retorno["anterior"] = None

    return retorno


@router.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao, dados_json FROM historico_comparativo_despesas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    
    resultado = []
    for r in rows:
        resultado.append({
            "id": r[0], 
            "periodo": r[1], 
            "data_geracao": r[2], 
            "dados": r[3]
        })
        
    return resultado



@router.get("/historico_comparativo_despesas/{id}")
def get_historico_comparativo_despesas_id(id: int):
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, dados_json FROM historico_comparativo_despesas WHERE id = %s", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": row[2]  # Retorna a string JSON
    }


@router.post("/api/comparativo_despesas_v2/{periodo}/salvar")

@router.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    from pc_backend.app.config import PG_CONFIG
    
    try:
        body = await request.json()
        ids = body.get("ids", [])
        
        if not ids:
            return {"ok": False, "mensagem": "Nenhum ID fornecido."}
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(ids))
        cur.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
        excluidos = cur.rowcount
        conn.commit()
        conn.close()
        
        return {"ok": True, "excluidos": excluidos}
    except Exception as e:
        print(f"[ERRO] Falha ao excluir históricos: {e}")
        return {"ok": False, "mensagem": str(e)}

@router.get("/gerar_pdf_comparativo_despesas")
def gerar_pdf_comparativo_despesas(request: Request, periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    base_url = str(request.base_url).rstrip("/")
    if "testserver" in base_url:
        base_url = os.getenv("PC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    from playwright.sync_api import sync_playwright
    from fastapi import Request
    from fastapi.responses import Response
    import time, os
    if historico_id:
        url = f"{base_url}/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"{base_url}/relatorio_comparativo_despesas_v2?periodo={periodo}&_t={int(time.time())}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_despesas_{periodo}.pdf"})


@router.get("/gerar_pdf_comparativo_despesas/{historico_id}")
def gerar_pdf_comparativo_despesas_por_id(request: Request, historico_id: int, periodo: str = "2026-TRIMESTRE-3"):
    return gerar_pdf_comparativo_despesas(request=request, periodo=periodo, historico_id=historico_id)
