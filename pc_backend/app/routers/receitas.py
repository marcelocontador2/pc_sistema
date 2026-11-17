# -*- coding: utf-8 -*-
"""
Rotas de Comparativo de Receitas.
Extraído do main.py para refatoração.
"""

import os
import json
import datetime
import sqlite3
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
DB_PATH = os.path.join(BASE_DIR, "pc_storage", "banco_dados.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

# =========================================================
# FUNÇÃO AUXILIAR
# =========================================================
def api_comparativo_receitas_v2(periodo: str):
    import os

    upload_dir = UPLOAD_DIR

    def parse_valor(s):
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try:
            return float(s)
        except:
            return 0.0

    def parse_pct(s):
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try:
            return float(s)
        except:
            return 0.0

    def ler_csv(p):
        if not p:
            return None
        periodo_formatado = p.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_RECEITAS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_RECEITAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return None

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f:
                    linhas = f.readlines()

            dados = {
                "orcado_total": 0.0,
                "realizado_total": 0.0,
                "percentual_total": 0.0,
                "grupos": [],
                "cores": []
            }

            grupos_nomes = ["RECEITAS DE CONTRIBUIÇÕES", "RECEITAS PATRIMONIAIS", "RECEITAS DE SERVIÇOS", "TRANSFERÊNCIAS CORRENTES", "OUTRAS RECEITAS CORRENTES", "RECEITAS DE CAPITAL"]

            for linha in linhas:
                if ";" not in linha:
                    continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4:
                    continue

                nome = partes_linha[0].strip().strip('"')
                if not nome:
                    continue

                if nome == "RECEITA REALIZADA":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["realizado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])

                elif nome in grupos_nomes:
                    orc_v = parse_valor(partes_linha[1])
                    real_v = parse_valor(partes_linha[2])
                    pct_v = parse_pct(partes_linha[3])
                    # Inclui TODOS os grupos, mesmo zerados
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": orc_v,
                        "realizado": real_v,
                        "percentual": pct_v
                    })

                elif nome.upper().startswith("COREN "):
                    dados["cores"].append({
                        "nome": nome.replace("COREN ", "").strip(),
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })

            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV {arquivo}: {e}")
            return None

    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0])
        tipo = partes[1]
        valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": f"Dados não encontrados para o período {periodo}."}

    retorno = {
        "orcado_total": atual["orcado_total"],
        "realizado_total": atual["realizado_total"],
        "percentual_total": atual["percentual_total"],
        "grupos": atual["grupos"],
        "cores": atual["cores"]
    }

    if anterior:
        retorno["anterior"] = {
            "orcado_total": anterior["orcado_total"],
            "realizado_total": anterior["realizado_total"],
            "percentual_total": anterior["percentual_total"],
            "grupos": anterior["grupos"]
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, dados_json FROM historico_comparativo_receitas WHERE id = ?", (id,))
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
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)",
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
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        placeholders = ",".join(["?"] * len(ids))
        cur.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
        excluidos = cur.rowcount
        conn.commit()
        conn.close()
        return {"ok": True, "excluidos": excluidos}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os

    if historico_id:
        url = f"http://127.0.0.1:994/relatorio_comparativo_receitas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:994/relatorio_comparativo_receitas_v2?periodo={periodo}&_t={int(time.time())}"

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
def gerar_pdf_comparativo_receitas_por_id(historico_id: int, periodo: str = "2026-TRIMESTRE-3"):
    return gerar_pdf_comparativo_receitas(periodo=periodo, historico_id=historico_id)
