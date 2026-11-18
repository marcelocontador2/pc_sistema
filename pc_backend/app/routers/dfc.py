"""
Rota da DFC - Leitura por Blocos (Operacional, Investimento, Financiamento).
"""
import csv
import os
from fastapi import APIRouter, HTTPException

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

def processar_dfc(caminho):
    linhas = []
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for row in leitor:
            linhas.append(row)

    # Funcao para achar o indice de um termo na coluna 0 ou 3
    def achar_idx(termo, inicio=0):
        termo = termo.upper().strip()
        for i in range(inicio, len(linhas)):
            p = linhas[i]
            if len(p) > 0 and termo in str(p[0]).upper():
                return i
            if len(p) > 3 and termo in str(p[3]).upper():
                return i
        return -1

    def val(p, idx):
        if p and len(p) > idx:
            return limpar(p[idx])
        return 0.0

    # --- ENCONTRA OS MARCOS (BLOCOS) ---
    idx_oper = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DAS OPERA")
    idx_invest = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO")
    idx_financ = achar_idx("FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO")
    idx_apuracao = achar_idx("APURA")

    if idx_oper == -1 or idx_invest == -1 or idx_financ == -1 or idx_apuracao == -1:
        return {"erro": "estrutura", "mensagem": "Nao foi possivel localizar os blocos da DFC no CSV."}

    # --- BLOCO OPERACIONAL ---
    linhas_oper = linhas[idx_oper:idx_invest]
    def buscar_no_bloco(bloco, termo):
        termo = termo.upper().strip()
        for p in bloco:
            if len(p) > 0 and termo in str(p[0]).upper():
                return p
            if len(p) > 3 and termo in str(p[3]).upper():
                return p
        return None

    l_ing_oper = buscar_no_bloco(linhas_oper, "INGRESSOS")
    l_desemb_oper = buscar_no_bloco(linhas_oper, "DESEMBOLSOS")
    l_liq_oper = buscar_no_bloco(linhas_oper, "FLUXO DE CAIXA L")

    # --- BLOCO INVESTIMENTO ---
    linhas_invest = linhas[idx_invest:idx_financ]
    l_ing_invest = buscar_no_bloco(linhas_invest, "INGRESSOS")
    l_desemb_invest = buscar_no_bloco(linhas_invest, "DESEMBOLSOS")
    l_liq_invest = buscar_no_bloco(linhas_invest, "FLUXO DE CAIXA L")

    # --- BLOCO FINANCIAMENTO ---
    linhas_financ = linhas[idx_financ:idx_apuracao]
    l_ing_financ = buscar_no_bloco(linhas_financ, "INGRESSOS")
    l_desemb_financ = buscar_no_bloco(linhas_financ, "DESEMBOLSOS")
    l_liq_financ = buscar_no_bloco(linhas_financ, "FLUXO DE CAIXA L")

    # --- APURACAO ---
    linhas_apuracao = linhas[idx_apuracao:]
    l_geracao = buscar_no_bloco(linhas_apuracao, "GERA")
    l_caixa_inicial = buscar_no_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA INICIAL")
    l_caixa_final = buscar_no_bloco(linhas_apuracao, "CAIXA E EQUIVALENTES DE CAIXA FINAL")

    dados = {
        "operacional": {
            "ingressos": {"atual": val(l_ing_oper, 3), "anterior": val(l_ing_oper, 4)},
            "desembolsos": {"atual": val(l_desemb_oper, 3), "anterior": val(l_desemb_oper, 4)},
            "liquido": {"atual": val(l_liq_oper, 3), "anterior": val(l_liq_oper, 4)},
        },
        "investimento": {
            "ingressos": {"atual": val(l_ing_invest, 3), "anterior": val(l_ing_invest, 4)},
            "desembolsos": {"atual": val(l_desemb_invest, 3), "anterior": val(l_desemb_invest, 4)},
            "liquido": {"atual": val(l_liq_invest, 3), "anterior": val(l_liq_invest, 4)},
        },
        "financiamento": {
            "ingressos": {"atual": val(l_ing_financ, 3), "anterior": val(l_ing_financ, 4)},
            "desembolsos": {"atual": val(l_desemb_financ, 3), "anterior": val(l_desemb_financ, 4)},
            "liquido": {"atual": val(l_liq_financ, 3), "anterior": val(l_liq_financ, 4)},
        },
        "caixa": {
            "geracao": {"atual": val(l_geracao, 3), "anterior": val(l_geracao, 4)},
            "inicial": {"atual": val(l_caixa_inicial, 3), "anterior": val(l_caixa_inicial, 4)},
            "final": {"atual": val(l_caixa_final, 3), "anterior": val(l_caixa_final, 4)},
        }
    }
    return {"erro": False, "dados": dados}


# ============================================================
# Rota para servir a tela HTML do DFC
# ============================================================
from fastapi.responses import FileResponse
import os

@router.get("/analise_dfc")
async def serve_analise_dfc():
    caminho = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "pc_frontend",
        "analise_dfc.html"
    )
    if os.path.exists(caminho):
        return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})
    return {"erro": "Arquivo HTML nao encontrado", "caminho": caminho}

# ============================================================
# ROTAS DE SALVAR, HISTÃ“RICO E PDF (PostgreSQL)
# ============================================================
import json
from datetime import datetime
from fastapi import Response
import psycopg2
from pc_backend.app.config import PG_CONFIG


@router.post("/salvar/{periodo}/{periodo_anterior}")
async def salvar_analise_dfc(periodo: str, periodo_anterior: str):
    try:
        # Chama a funÃ§Ã£o de processamento do DFC
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"DFC_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"ok": False, "mensagem": f"CSV nao encontrado: DFC_{p_limpo}.csv"}
        
        resultado = processar_dfc(caminho)
        if resultado.get("erro"):
            return {"ok": False, "mensagem": resultado.get("mensagem", "Erro no processamento")}
        
        dados_json = resultado["dados"]
        periodo_label = f"{periodo} vs {periodo_anterior}"
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historico_analise_dfc (periodo, data_geracao, resultado_json)
            VALUES (%s, NOW(), %s) RETURNING id
        """, (periodo_label, json.dumps(dados_json)))
        new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        print(f"[DFC] Erro ao salvar: {e}")
        return {"ok": False, "mensagem": str(e)}


@router.get("/historico")
async def get_historico_dfc():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dfc ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[DFC] Erro ao listar historico: {e}")
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
            return {"erro": True, "mensagem": "Nao encontrado"}
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
def gerar_pdf_analise_dfc(id: int):
    import traceback
    try:
        from playwright.sync_api import sync_playwright
        import time
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_dfc WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)
        
        periodo_label = row[0]
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        
        url = "http://127.0.0.1:994/analise_dfc?id=" + str(id) + "&_t=" + str(int(time.time()))
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.evaluate("() => { const el = document.querySelector('.top-bar, .filtros, .sidebar, .btn'); if (el) el.style.display = 'none'; }")
            page.add_style_tag(content="button, select, .top-bar, .filtros, .sidebar { display: none !important; }")
            page.wait_for_timeout(1000)
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


# ============================================================
# ROTA GENÉRICA: /{periodo} (deve ficar no FINAL para não conflitar)
# ============================================================
@router.get("/{periodo}")
def api_analise_dfc(periodo: str):
    try:
        p_limpo = periodo.replace("-", "_")
        caminho = os.path.join(UPLOADS_DIR, f"DFC_{p_limpo}.csv")
        if not os.path.exists(caminho):
            return {"erro": "faltando", "mensagem": f"CSV nao encontrado: DFC_{p_limpo}.csv"}
        return processar_dfc(caminho)
    except Exception as e:
        import traceback
        print(f"[DFC] ERRO: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}
