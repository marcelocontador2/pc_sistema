# -*- coding: utf-8 -*-
import os, json, glob, csv, logging
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
import psycopg2
from pc_backend.app.config import PG_CONFIG

logger = logging.getLogger("analise_financeira_bf")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()


def _parse_val(v):
    if not v:
        return 0.0
    v = v.replace(".", "").replace(",", ".").replace("R$", "").strip()
    try:
        return float(v)
    except ValueError:
        return 0.0






def _ler_balanco(periodo_str):
    periodo_formatado = periodo_str.replace("-", "_")
    padrao = os.path.join(UPLOAD_DIR, "*BALANCO_FINANCEIRO*" + periodo_formatado + "*.csv")
    arquivos = sorted(glob.glob(padrao))
    if not arquivos:
        return None
    arquivo = arquivos[0]
    
    res = {
        "receitas": {"corrente": 0.0, "capital": 0.0, "total": 0.0},
        "despesas": {"corrente": 0.0, "capital": 0.0, "total": 0.0},
        "extra": {"recebimentos": 0.0, "pagamentos": 0.0},
        "caixa": {"saldo_anterior": 0.0, "geracao_liquida": 0.0, "saldo_seguinte": 0.0},
    }
    # Dicionário auxiliar para o período anterior (coluna 2 do CSV)
    res_ant = {
        "receitas": {"corrente": 0.0, "capital": 0.0, "total": 0.0},
        "despesas": {"corrente": 0.0, "capital": 0.0, "total": 0.0},
        "extra": {"recebimentos": 0.0, "pagamentos": 0.0},
        "caixa": {"saldo_anterior": 0.0, "geracao_liquida": 0.0, "saldo_seguinte": 0.0},
    }
    
    with open(arquivo, "r", encoding="latin-1") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    
    for linha in linhas:
        if not linha:
            continue
        
        cols = [c.strip() for c in linha]
        if len(cols) < 3:
            continue
        
        # Limpa quebras de linha e acentos
        nome_esq = " ".join(cols[0].upper().split())
        val_esq = _parse_val(cols[1]) if len(cols) > 1 else 0.0
        val_esq_ant = _parse_val(cols[2]) if len(cols) > 2 else 0.0  # COLUNA 2 = EXERCÍCIO ANTERIOR
        
        # --- RECEITAS E CAIXA (Coluna Esquerda) ---
        if nome_esq == "RECEITAS CORRENTE":
            res["receitas"]["corrente"] = val_esq
            res_ant["receitas"]["corrente"] = val_esq_ant
        elif nome_esq == "RECEITAS DE CAPITAL":
            res["receitas"]["capital"] = val_esq
            res_ant["receitas"]["capital"] = val_esq_ant
        elif "SALDO EM ESPÉCIE" in nome_esq and "ANTERIOR" in nome_esq:
            res["caixa"]["saldo_anterior"] = val_esq
            res_ant["caixa"]["saldo_anterior"] = val_esq_ant
        elif nome_esq == "RECEBIMENTOS EXTRAORÇAMENTÁRIOS":
            res["extra"]["recebimentos"] = val_esq
            res_ant["extra"]["recebimentos"] = val_esq_ant
        
        # --- DESPESAS E CAIXA (Coluna Direita, cols 3 e 4) ---
        if len(cols) >= 6:
            nome_dir = " ".join(cols[3].upper().split())
            val_dir = _parse_val(cols[4])
            val_dir_ant = _parse_val(cols[5]) if len(cols) > 5 else 0.0  # COLUNA 5 = EXERCÍCIO ANTERIOR
            
            if nome_dir == "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE":
                res["despesas"]["corrente"] = val_dir
                res_ant["despesas"]["corrente"] = val_dir_ant
            elif nome_dir == "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CAPITAL":
                res["despesas"]["capital"] = val_dir
                res_ant["despesas"]["capital"] = val_dir_ant
            elif nome_dir == "PAGAMENTOS EXTRAORÇAMENTÁRIOS":
                res["extra"]["pagamentos"] = val_dir
                res_ant["extra"]["pagamentos"] = val_dir_ant
            elif "SALDO EM ESPÉCIE" in nome_dir and "SEGUINTE" in nome_dir:
                res["caixa"]["saldo_seguinte"] = val_dir
                res_ant["caixa"]["saldo_seguinte"] = val_dir_ant
    
    # Calcula totais (atual)
    res["receitas"]["total"] = res["receitas"]["corrente"] + res["receitas"]["capital"]
    res["despesas"]["total"] = res["despesas"]["corrente"] + res["despesas"]["capital"]
    res["caixa"]["geracao_liquida"] = res["caixa"]["saldo_seguinte"] - res["caixa"]["saldo_anterior"]
    
    # Calcula totais (anterior)
    res_ant["receitas"]["total"] = res_ant["receitas"]["corrente"] + res_ant["receitas"]["capital"]
    res_ant["despesas"]["total"] = res_ant["despesas"]["corrente"] + res_ant["despesas"]["capital"]
    res_ant["caixa"]["geracao_liquida"] = res_ant["caixa"]["saldo_seguinte"] - res_ant["caixa"]["saldo_anterior"]
    
    return res, res_ant


def _montar_json_aninhado(dados_atual, dados_anterior):
    return {
        "receitas": {
            "corrente": {"atual": dados_atual["receitas"]["corrente"], "anterior": dados_anterior["receitas"]["corrente"]},
            "capital":  {"atual": dados_atual["receitas"]["capital"],  "anterior": dados_anterior["receitas"]["capital"]},
            "total":    {"atual": dados_atual["receitas"]["total"],    "anterior": dados_anterior["receitas"]["total"]},
        },
        "despesas": {
            "corrente": {"atual": dados_atual["despesas"]["corrente"], "anterior": dados_anterior["despesas"]["corrente"]},
            "capital":  {"atual": dados_atual["despesas"]["capital"],  "anterior": dados_anterior["despesas"]["capital"]},
            "total":    {"atual": dados_atual["despesas"]["total"],    "anterior": dados_anterior["despesas"]["total"]},
        },
        "extra": {
            "recebimentos": {"atual": dados_atual["extra"]["recebimentos"], "anterior": dados_anterior["extra"]["recebimentos"]},
            "pagamentos":   {"atual": dados_atual["extra"]["pagamentos"],   "anterior": dados_anterior["extra"]["pagamentos"]},
        },
        "caixa": {
            "saldo_anterior":  {"atual": dados_atual["caixa"]["saldo_anterior"],  "anterior": dados_anterior["caixa"]["saldo_anterior"]},
            "geracao_liquida": {"atual": dados_atual["caixa"]["geracao_liquida"], "anterior": dados_anterior["caixa"]["geracao_liquida"]},
            "saldo_seguinte":  {"atual": dados_atual["caixa"]["saldo_seguinte"],  "anterior": dados_anterior["caixa"]["saldo_seguinte"]},
        },
    }





@router.get("/api/analise_financeira_bf/{periodo}")
@router.get("/api/analise_financeira_bf/{periodo}/{periodo_anterior_ignorado}")
def api_analise_financeira_bf(periodo: str, periodo_anterior_ignorado: str = None):
    try:
        # O período anterior agora vem do MESMO CSV (coluna Exercício Anterior)
        # O parâmetro da URL é ignorado (mantido por compatibilidade)
        partes = periodo.split(" vs ")
        periodo_atual = partes[0].strip() if partes else periodo

        resultado = _ler_balanco(periodo_atual)
        if not resultado:
            return {"erro": True, "mensagem": "Balanco Financeiro nao encontrado para " + periodo_atual}
        
        dados_atual, dados_anterior = resultado
        return {"erro": False, "dados": _montar_json_aninhado(dados_atual, dados_anterior)}
    except Exception as e:
        logger.exception("Erro em api_analise_financeira_bf")
        return {"erro": True, "mensagem": str(e)}



@router.post("/salvar_analise_financeira_bf/{periodo}/{periodo_anterior}")
def salvar_analise_financeira_bf(periodo: str, periodo_anterior: str):
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
def get_historico_analise_financeira_bf():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_financeira_bf ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception:
        logger.exception("Erro em get_historico")
        return []


@router.get("/historico_analise_financeira_bf/{id}")
def get_historico_analise_financeira_bf_id(id: int):
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
def excluir_analise_financeira_bf(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_financeira_bf WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/analise_financeira_bf")
def serve_analise_financeira_bf():
    caminho = os.path.join(FRONTEND_DIR, "analise_financeira_bf.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": "Arquivo HTML nao encontrado"}





@router.get("/gerar_pdf_analise_financeira_bf/{id}")
def gerar_pdf_analise_financeira_bf(id: int):
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
    def get_val(path, lado="atual"):
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

    def fmt(v):
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
