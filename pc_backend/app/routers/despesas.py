# -*- coding: utf-8 -*-
"""
Rotas de Comparativo de Despesas.
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

router = APIRouter()

def api_comparativo_despesas_v2(periodo: str):
    import os, unicodedata
    upload_dir = UPLOAD_DIR

    partes = periodo.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None

    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0

    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0

    def normalizar(txt):
        return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8').strip().upper()

    def ler_csv(periodo):
        if not periodo: return None
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_DESPESAS_{periodo_formatado}.csv")

        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_DESPESAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break

        if not os.path.exists(arquivo):
            return None

        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f: linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f: linhas = f.readlines()

            dados = {
                "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
                "percentual_total": 0.0, "grupos": [], "detalhes": []
            }

            # Lista fixa de cabeçalhos que NíƒO são contas analí­ticas
            cabecalhos = [
                "CREDITO DISPONIVEL", "CREDITO DISPONIVEL - DESPESA CORRENTE",
                "CREDITO DISPONIVEL - DESPESA CAPITAL",
                "PESSOAL E ENCARGOS SOCIAIS", "JUROS E ENCARGOS DA DIVIDA",
                "OUTRAS DESPESAS CORRENTES", "INVESTIMENTOS",
                "INVERSOES FINANCEIRAS", "AMORTIZACAO DA DIVIDA",
                "APLICACOES DIRETAS", "APLICACOES INDIRETAS",
                "OUTROS SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "DEMAIS SERVICOS - PESSOAS JURIDICAS",
                "APOSENTADORIAS DO RPPS", "PROVENTOS - PESSOAL CIVIL",
                "VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL",
                "OUTRAS DESPESAS VARIAVEIS - PESSOAL CIVIL - RGPS",
                "RESSARCIMENTO DE DESPESAS DE PESSOAL REQUISITADO",
                "JUROS SOBRE A DIVIDA POR CONTRATO",
                "JUROS DE SOBRE FORNECIMENTO DE BENS",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA JURIDICA",
                "JUROS DE SERVICOS DE TERCEIROS - PESSOA FISICA",
                "OUTROS JUROS E ENCARGOS DE MORA",
                "DESPESAS DE EXERCICIOS ANTERIORES (JUROS E ENCARGOS DAS DIVIDAS)",
                "OUTRAS DESPESAS DE PESSOAL DECORRENTES DE CONTRATOS DE TERCEIROS",
                "OUTRAS DESPESAS CORRENTES - APLICACOES DIRETAS",
                "INVESTIMENTOS - APLICACOES DIRETAS",
                "INVERSOES FINANCEIRAS - APLICACOES DIRETAS",
                "AMORTIZACAO DA DIVIDA - APLICACOES DIRETAS",
                "TOTAL", "TOTAL GERAL"
            ]
            cabecalhos_norm = [normalizar(cg) for cg in cabecalhos]

            detalhes_temp = []

            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue

                nome_original = partes_linha[0].strip().strip('"')
                nome_norm = normalizar(nome_original)

                if not nome_original or len(nome_original) < 3: continue

                # Total Global
                if nome_norm == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])

                # Grupos contábeis
                grupos_alvo_norm = [
                    "PESSOAL E ENCARGOS SOCIAIS",
                    "JUROS E ENCARGOS DA DIVIDA",
                    "OUTRAS DESPESAS CORRENTES",
                    "INVESTIMENTOS",
                    "INVERSOES FINANCEIRAS",
                    "AMORTIZACAO DA DIVIDA"
                ]
                if nome_norm in grupos_alvo_norm:
                    if not any(g["nome"] == nome_original for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })

                # Detalhes: exclui cabeçalhos e pega o resto com valor > 0
                valor_emp = parse_valor(partes_linha[2])
                if valor_emp > 0 and nome_norm not in cabecalhos_norm:
                    # Exclui também linhas com "TOTAL" no nome (são somatí³rios)
                    if "TOTAL" not in nome_norm and "SUBTOTAL" not in nome_norm:
                        detalhes_temp.append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": valor_emp,
                            "percentual": parse_pct(partes_linha[3])
                        })

            # Ordena por empenhado desc e pega top 10
            detalhes_temp.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = detalhes_temp[:10]

            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None

    atual = ler_csv(periodo)
    anterior = ler_csv(periodo_anterior)

    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}

    return {
        "erro": False,
        "periodo": periodo,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": [], "detalhes": []
        }
    }

@router.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, dados_json FROM historico_comparativo_despesas WHERE id = ?", (id,))
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
    
    from .config import PG_CONFIG
    
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
def gerar_pdf_comparativo_despesas(periodo: str = "2026-TRIMESTRE-3", historico_id: int = None):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    if historico_id:
        url = f"http://127.0.0.1:994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:994/relatorio_comparativo_despesas_v2?periodo={periodo}&_t={int(time.time())}"
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
def gerar_pdf_comparativo_despesas_por_id(historico_id: int, periodo: str = "2026-TRIMESTRE-3"):
    return gerar_pdf_comparativo_despesas(periodo=periodo, historico_id=historico_id)
