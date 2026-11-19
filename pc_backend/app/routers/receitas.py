from pc_backend.app.config import PG_CONFIG
import psycopg2
# -*- coding: utf-8 -*-
"""
Rotas de Comparativo de Receitas.
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
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

from pc_backend.app.db_memoria import salvar_contas_memoria, carregar_contas_memoria, _slug_conta

def _persistir_receitas_memoria(periodo: str, dados: dict) -> None:
    if not periodo or not isinstance(dados, dict):
        return
    itens = []
    itens.append({
        "chave": "receita_realizada_total",
        "descricao": "RECEITA REALIZADA",
        "valor": float(dados.get("realizado_total") or 0.0),
        "extra": {
            "tipo": "total",
            "orcado": float(dados.get("orcado_total") or 0.0),
            "realizado": float(dados.get("realizado_total") or 0.0),
            "percentual": float(dados.get("percentual_total") or 0.0),
        },
    })
    for idx, g in enumerate(dados.get("grupos") or []):
        if isinstance(g, dict):
            nome = str(g.get("nome") or f"grupo_{idx+1}").strip()
            itens.append({
                "chave": f"grupo_{_slug_conta(nome)}",
                "descricao": nome,
                "valor": float(g.get("realizado") or 0.0),
                "extra": {"tipo": "grupo", "nome": nome, "orcado": float(g.get("orcado") or 0.0), "realizado": float(g.get("realizado") or 0.0), "percentual": float(g.get("percentual") or 0.0)},
            })
    for idx, c in enumerate(dados.get("cores") or []):
        if isinstance(c, dict):
            nome = str(c.get("nome") or f"coren_{idx+1}").strip()
            itens.append({
                "chave": f"coren_{_slug_conta(nome)}",
                "descricao": f"COREN {nome}",
                "valor": float(c.get("realizado") or 0.0),
                "extra": {"tipo": "coren", "nome": nome, "orcado": float(c.get("orcado") or 0.0), "realizado": float(c.get("realizado") or 0.0), "percentual": float(c.get("percentual") or 0.0)},
            })
    try:
        salvar_contas_memoria("COMPARATIVO_RECEITAS", periodo, itens)
    except Exception as e:
        print(f"[RECEITAS] Aviso ao salvar memoria PG: {e}")

def _carregar_receitas_memoria(periodo: str) -> dict | None:
    mem = carregar_contas_memoria("COMPARATIVO_RECEITAS", periodo)
    if not mem:
        return None
    dados = {
        "orcado_total": 0.0,
        "realizado_total": 0.0,
        "percentual_total": 0.0,
        "grupos": [],
        "cores": [],
    }
    for item in mem:
        extra = item.get("dados_json") if isinstance(item.get("dados_json"), dict) else {}
        tipo = extra.get("tipo")
        if tipo == "total" or item.get("chave") == "receita_realizada_total":
            dados["orcado_total"] = float(extra.get("orcado") or 0.0)
            dados["realizado_total"] = float(extra.get("realizado") if extra.get("realizado") is not None else (item.get("valor") or 0.0))
            dados["percentual_total"] = float(extra.get("percentual") or 0.0)
        elif tipo == "grupo":
            dados["grupos"].append({
                "nome": extra.get("nome") or item.get("descricao"),
                "orcado": float(extra.get("orcado") or 0.0),
                "realizado": float(extra.get("realizado") if extra.get("realizado") is not None else (item.get("valor") or 0.0)),
                "percentual": float(extra.get("percentual") or 0.0),
            })
        elif tipo == "coren":
            dados["cores"].append({
                "nome": extra.get("nome") or item.get("descricao"),
                "orcado": float(extra.get("orcado") or 0.0),
                "realizado": float(extra.get("realizado") if extra.get("realizado") is not None else (item.get("valor") or 0.0)),
                "percentual": float(extra.get("percentual") or 0.0),
            })
    return dados


# =========================================================
# FUNÇÃO AUXILIAR
# =========================================================
def _buscar_receitas_pg(p: str) -> dict | None:
    if not p:
        return None
    mem = _carregar_receitas_memoria(p)
    if mem and (mem.get("realizado_total") or mem.get("orcado_total") or mem.get("grupos") or mem.get("cores")):
        return mem

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT dados_json FROM historico_comparativo_receitas WHERE periodo = %s ORDER BY id DESC LIMIT 1",
            (p,),
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                "SELECT dados_json FROM historico_comparativo_receitas WHERE periodo ILIKE %s ORDER BY id DESC LIMIT 1",
                (f"%{p}%",),
            )
            row = cur.fetchone()
        if not row or not row[0]:
            return None
        dj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        if not isinstance(dj, dict):
            return None
        dados = {
            "orcado_total": float(dj.get("orcado_total") or 0.0),
            "realizado_total": float(dj.get("realizado_total") or 0.0),
            "percentual_total": float(dj.get("percentual_total") or 0.0),
            "grupos": dj.get("grupos") or [],
            "cores": dj.get("cores") or [],
            "anterior": dj.get("anterior"),
        }
        _persistir_receitas_memoria(p, dados)
        return dados
    except Exception as e:
        print(f"[RECEITAS] Erro ao consultar PostgreSQL ({p}): {e}")
        return None
    finally:
        conn.close()


def api_comparativo_receitas_v2(periodo: str):
    atual = _buscar_receitas_pg(periodo)
    if not atual:
        return {"erro": True, "mensagem": f"Dados de receitas n?o encontrados no PostgreSQL para o per?odo {periodo}."}

    anterior = atual.get("anterior")
    if not anterior:
        partes = periodo.split("-")
        if len(partes) == 3:
            try:
                periodo_anterior = f"{int(partes[0]) - 1}-{partes[1]}-{partes[2]}"
                anterior = _buscar_receitas_pg(periodo_anterior)
            except Exception:
                anterior = None

    retorno = {
        "orcado_total": atual.get("orcado_total", 0.0),
        "realizado_total": atual.get("realizado_total", 0.0),
        "percentual_total": atual.get("percentual_total", 0.0),
        "grupos": atual.get("grupos", []),
        "cores": atual.get("cores", []),
    }

    if isinstance(anterior, dict):
        retorno["anterior"] = {
            "orcado_total": anterior.get("orcado_total", 0.0),
            "realizado_total": anterior.get("realizado_total", 0.0),
            "percentual_total": anterior.get("percentual_total", 0.0),
            "grupos": anterior.get("grupos", []),
        }
    else:
        retorno["anterior"] = None

    return retorno


# =========================================================

# =========================================================
# ROTAS DE RECEITAS
# =========================================================

@router.get("/api/comparativo_receitas/{periodo}")
def api_comparativo_receitas(periodo: str):
    # Implementação antiga (mantida para compatibilidade)
    return {"erro": True, "mensagem": "Use /api/comparativo_receitas_v2/{periodo}"}


@router.get("/historico_comparativo_receitas")
def get_historico_comparativo_receitas():
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao, dados_json FROM historico_comparativo_receitas ORDER BY id DESC")
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
    return Response(content=json.dumps(resultado), media_type="application/json")


@router.get("/historico_comparativo_receitas/{id}")
def get_historico_comparativo_receitas_id(id: int):
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, dados_json FROM historico_comparativo_receitas WHERE id = %s", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": row[2]  # Retorna a string JSON exata que está no banco
    }


@router.post("/api/comparativo_receitas_v2/{periodo}/salvar")
def salvar_comparativo_receitas(periodo: str):
    try:
        dados = api_comparativo_receitas_v2(periodo)
        if dados.get("erro"):
            return dados
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
            id SERIAL PRIMARY KEY, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (%s, %s, %s)",
                    (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
    import psycopg2
    try:
        body = await request.json()
        ids = body.get("ids", [])
        if not ids:
            return {"ok": False, "mensagem": "Nenhum ID fornecido."}
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(ids))
        cur.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
        excluidos = cur.rowcount
        conn.commit()
        conn.close()
        return {"ok": True, "excluidos": excluidos}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(request: Request, periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    base_url = str(request.base_url).rstrip("/")
    from playwright.sync_api import sync_playwright
    from fastapi import Request
    from fastapi.responses import Response
    import time, os

    if historico_id:
        url = f"{base_url}/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"{base_url}/relatorio_comparativo_receitas_v2?periodo={periodo}&_t={int(time.time())}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        # Espera o texto "Carregando..." desaparecer
        try:
            page.wait_for_selector("text=Carregando...", state="detached", timeout=10000)
        except:
            pass
        page.wait_for_timeout(2000)
        
        # Força a impressão de tela para não cortar os gráficos
        page.emulate_media(media="screen")
        
        # Espera até 10 segundos para os elementos com valores carregarem
        try:
            page.wait_for_function("() => { const els = document.querySelectorAll('div, span, td'); return Array.from(els).some(e => e.innerText.includes('R$') && !e.innerText.includes('0,00')); }", timeout=10000)
        except:
            pass
        page.wait_for_timeout(2000)
        page.evaluate("""() => {
            document.querySelectorAll('canvas').forEach(canvas => {
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.className = 'canvas-img';
                img.style.cssText = 'display: block; max-width: 100%; max-height: 240px; margin: 0 auto;';
                canvas.parentNode.insertBefore(img, canvas.nextSibling);
            });
        }""")
        page.screenshot(path="debug_receitas.png", full_page=True)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_receitas_{periodo}.pdf"}
    )


@router.get("/gerar_pdf_comparativo_receitas/{historico_id}")
def gerar_pdf_comparativo_receitas_por_id(request: Request, historico_id: int, periodo: str = "2026-TRIMESTRE-3"):
    return gerar_pdf_comparativo_receitas(request=request, periodo=periodo, historico_id=historico_id)
