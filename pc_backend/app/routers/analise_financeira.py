# -*- coding: utf-8 -*-
import os, json, glob, csv, logging
from fastapi import APIRouter, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
from fastapi.responses import FileResponse
import psycopg2
from pc_backend.app.config import PG_CONFIG

logger = logging.getLogger("analise_financeira_bf")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()


def _parse_val(v, request: Request = None):
    if not v:
        return 0.0
    v = v.replace(".", "").replace(",", ".").replace("R$", "").strip()
    try:
        return float(v)
    except ValueError:
        return 0.0






def _buscar_balanco_pg(periodo_str: str, periodo_ant: str | None = None, request: Request = None) -> dict | None:
    __ent_id = resolver_entidade_id(request)
    if not periodo_str:
        return None
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        if periodo_ant:
            label = f"{periodo_str} vs {periodo_ant}"
            cur.execute(
                "SELECT resultado_json FROM historico_analise_financeira_bf WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
                (label, __ent_id, __ent_id),
            )
            row = cur.fetchone()
            if row and row[0]:
                return row[0] if isinstance(row[0], dict) else json.loads(row[0])

        cur.execute(
            "SELECT resultado_json FROM historico_analise_financeira_bf WHERE (periodo = %s OR periodo LIKE %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (periodo_str, f"{periodo_str} vs %", __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if not row or not row[0]:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    except Exception:
        logger.exception("Erro ao consultar historico_analise_financeira_bf no PostgreSQL")
        return None
    finally:
        conn.close()


@router.get("/api/analise_financeira_bf/{periodo}")
@router.get("/api/analise_financeira_bf/{periodo}/{periodo_anterior}")
def api_analise_financeira_bf(periodo: str, periodo_anterior: str = None, request: Request = None):
    try:
        partes = periodo.split(" vs ")
        periodo_atual = partes[0].strip() if partes else periodo
        ant = periodo_anterior or (partes[1].strip() if len(partes) > 1 else None)

        dados = _buscar_balanco_pg(periodo_atual, ant)
        if not dados:
            return {"erro": True, "mensagem": "Balanco Financeiro nao encontrado no PostgreSQL para " + periodo_atual}

        return {"erro": False, "dados": dados}
    except Exception as e:
        logger.exception("Erro em api_analise_financeira_bf")
        return {"erro": True, "mensagem": str(e)}


@router.post("/salvar_analise_financeira_bf/{periodo}/{periodo_anterior}")
def salvar_analise_financeira_bf(periodo: str, periodo_anterior: str, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    """AGORA SALVA DE VERDADE no Postgres."""
    try:
        resultado = api_analise_financeira_bf(periodo, periodo_anterior)
        if resultado.get("erro"):
            return resultado

        dados_json = resultado["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"

        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO historico_analise_financeira_bf (periodo, data_geracao, resultado_json) "
            "VALUES (%s, NOW(), %s) RETURNING id",
            (periodo_label, json.dumps(dados_json)),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()

        logger.warning(f"[SALVAR] id={new_id} periodo={periodo_label} OK")
        return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        logger.exception("Erro em salvar_analise_financeira_bf")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico_analise_financeira_bf")
def get_historico_analise_financeira_bf(request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_financeira_bf WHERE (%s IS NULL OR entidade_id = %s) ORDER BY id DESC", (__ent_id, __ent_id))
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception:
        logger.exception("Erro em get_historico")
        return []


@router.get("/historico_analise_financeira_bf/{id}")
def get_historico_analise_financeira_bf_id(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_financeira_bf WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        logger.exception("Erro em get_historico_id")
        return {"erro": True, "mensagem": str(e)}


@router.delete("/excluir_analise_financeira_bf/{id}")
def excluir_analise_financeira_bf(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_financeira_bf WHERE (id = %s) AND (%s IS NULL OR entidade_id = %s)", (id, __ent_id, __ent_id))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/analise_financeira_bf")
def serve_analise_financeira_bf(request: Request = None):
    caminho = os.path.join(FRONTEND_DIR, "analise_financeira_bf.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": "Arquivo HTML nao encontrado"}





@router.get("/gerar_pdf_analise_financeira_bf/{id}")
def gerar_pdf_analise_financeira_bf(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    from playwright.sync_api import sync_playwright
    import time

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_analise_financeira_bf WHERE id = %s", (id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)

    periodo_label = row[0]
    dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])

    # Função auxiliar para extrair valores
    def get_val(path, lado="atual", request: Request = None):
        parts = path.split(".")
        cur = dados
        for p in parts:
            if cur and p in cur:
                cur = cur[p]
            else:
                return 0.0
        if isinstance(cur, dict):
            return cur.get(lado, 0.0)
        return cur or 0.0

    def fmt(v, request: Request = None):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- CÁLCULO DINÂMICO DOS TOTAIS (ATUAL E ANTERIOR) ---

    # Ingressos Atual = Receitas Total + Recebimentos Extra + Saldo Anterior
    total_ingressos_atual = (
        get_val("receitas.total") +
        get_val("extra.recebimentos") +
        get_val("caixa.saldo_anterior")
    )

    # Ingressos Anterior = Receitas Total Anterior + Recebimentos Extra Anterior + Saldo Anterior Anterior
    total_ingressos_ant = (
        get_val("receitas.total", "anterior") +
        get_val("extra.recebimentos", "anterior") +
        get_val("caixa.saldo_anterior", "anterior")
    )

    # Dispêndios Atual = Despesas Total + Pagamentos Extra + Saldo Seguinte
    total_dispendios_atual = (
        get_val("despesas.total") +
        get_val("extra.pagamentos") +
        get_val("caixa.saldo_seguinte")
    )

    # Dispêndios Anterior = Despesas Total Anterior + Pagamentos Extra Anterior + Saldo Seguinte Anterior
    total_dispendios_ant = (
        get_val("despesas.total", "anterior") +
        get_val("extra.pagamentos", "anterior") +
        get_val("caixa.saldo_seguinte", "anterior")
    )

    # Monta os valores do template
    valores = {
        "{{PERIODO}}": periodo_label,
        "{{RECEITAS_TOTAL}}": fmt(get_val("receitas.total")),
        "{{DESPESAS_TOTAL}}": fmt(get_val("despesas.total")),
        "{{CAIXA_SEGUINTE}}": fmt(get_val("caixa.saldo_seguinte")),
        "{{REC_CORRENTE}}": fmt(get_val("receitas.corrente")),
        "{{REC_CORRENTE_ANT}}": fmt(get_val("receitas.corrente", "anterior")),
        "{{REC_CAPITAL}}": fmt(get_val("receitas.capital")),
        "{{REC_CAPITAL_ANT}}": fmt(get_val("receitas.capital", "anterior")),
        "{{REC_TOTAL}}": fmt(get_val("receitas.total")),
        "{{REC_TOTAL_ANT}}": fmt(get_val("receitas.total", "anterior")),
        "{{DES_CORRENTE}}": fmt(get_val("despesas.corrente")),
        "{{DES_CORRENTE_ANT}}": fmt(get_val("despesas.corrente", "anterior")),
        "{{DES_CAPITAL}}": fmt(get_val("despesas.capital")),
        "{{DES_CAPITAL_ANT}}": fmt(get_val("despesas.capital", "anterior")),
        "{{DES_TOTAL}}": fmt(get_val("despesas.total")),
        "{{DES_TOTAL_ANT}}": fmt(get_val("despesas.total", "anterior")),
        "{{EXTRA_RECEB}}": fmt(get_val("extra.recebimentos")),
        "{{EXTRA_RECEB_ANT}}": fmt(get_val("extra.recebimentos", "anterior")),
        "{{EXTRA_PAG}}": fmt(get_val("extra.pagamentos")),
        "{{EXTRA_PAG_ANT}}": fmt(get_val("extra.pagamentos", "anterior")),
        "{{CAIXA_ANTERIOR}}": fmt(get_val("caixa.saldo_anterior")),
        "{{CAIXA_ANTERIOR_ANT}}": fmt(get_val("caixa.saldo_anterior", "anterior")),
        "{{CAIXA_GERACAO}}": fmt(get_val("caixa.geracao_liquida")),
        "{{CAIXA_GERACAO_ANT}}": fmt(get_val("caixa.geracao_liquida", "anterior")),
        "{{CAIXA_SEGUINTE_ANT}}": fmt(get_val("caixa.saldo_seguinte", "anterior")),
        "{{TOTAL_INGRESSOS}}": fmt(total_ingressos_atual),
        "{{TOTAL_INGRESSOS_ANT}}": fmt(total_ingressos_ant),
        "{{TOTAL_DISPENDIOS}}": fmt(total_dispendios_atual),
        "{{TOTAL_DISPENDIOS_ANT}}": fmt(total_dispendios_ant),
    }

    # Carrega o template e substitui os valores
    template_path = os.path.join(FRONTEND_DIR, "pdf_balanco_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    for k, v in valores.items():
        html = html.replace(k, str(v))

    # Gera o PDF com Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()

    logger.warning(f"[PDF] id={id} gerado com {len(pdf_bytes)} bytes (totais dinamicos)")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=balanco_financeiro_{id}.pdf"},
    )