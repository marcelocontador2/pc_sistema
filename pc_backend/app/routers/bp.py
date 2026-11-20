# -*- coding: utf-8 -*-
"""
Rota do BP (Balanço Patrimonial)
Criado em 18/11/2026, seguindo o padrão do DFC, DVP e DMPL.
"""
import csv
import os
import json
import traceback
from fastapi import APIRouter, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
import psycopg2
from pc_backend.app.config import PG_CONFIG

router = APIRouter(prefix="/api/analise_bp", tags=["bp"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")


def limpar(v):
    if not v:
        return 0.0
    v = str(v).replace("R$", "").strip()
    if v in ["-", "0,00", ""]:
        return 0.0
    if v.endswith("C"):
        v = v[:-1]
    if v.endswith("D"):
        v = v[:-1]
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    try:
        return float(v)
    except Exception:
        return 0.0


def processar_bp(caminho):
    """
    Processa o BP usando o modulo analise_bp (que le do banco, ja corrigido).
    O parametro 'caminho' e mantido por compatibilidade, mas nao e usado.
    """
    try:
        from pc_backend.app.analytics.analise_bp import analisar_bp
        resultado = analisar_bp()
        if not resultado:
            return {"erro": "interno", "mensagem": "analisar_bp retornou vazio"}
        
        # Montar os campos no formato esperado pelo frontend
        v2026 = resultado.get("2026", {})
        v2025 = resultado.get("2025", {})
        
        def campo(nome):
            return {
                "atual": v2026.get(nome, 0.0),
                "anterior": v2025.get(nome, 0.0)
            }
        
        dados = {
            "ativo_circulante": campo("Ativo Circulante"),
            "caixa": campo("Caixa e Equivalentes"),
            "superavit_financeiro": campo("Superavit Financeiro"),
            "estoques": campo("Estoques"),
            "creditos": campo("Creditos a Curto Prazo"),
            "ativo_nao_circulante": campo("Ativo Nao Circulante"),
            "ativo_realizavel": campo("Ativo Realizavel Longo Prazo"),
            "imobilizado": campo("Imobilizado"),
            "total_ativo": {
                "atual": resultado["totais"]["ativo_total_2026"],
                "anterior": resultado["totais"]["ativo_total_2025"]
            },
            "passivo_circulante": campo("Passivo Circulante"),
            "passivo_nao_circulante": campo("Passivo Nao Circulante"),
            "passivo_total": {
                "atual": resultado["totais"]["passivo_total_2026"],
                "anterior": resultado["totais"]["passivo_total_2025"]
            },
            "patrimonio_liquido": campo("Patrimonio Liquido"),
            "total_passivo": {
                "atual": resultado["totais"]["ativo_total_2026"],
                "anterior": resultado["totais"]["ativo_total_2025"]
            },
        }
        return {"erro": False, "dados": dados}
    except Exception as e:
        import traceback
        print(f"[BP] ERRO em processar_bp: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}





@router.get("/historico/{id}")
def get_historico_bp_id(id: int, request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        ent_id = resolver_entidade_id(request, conn=conn)
        if ent_id is not None:
            cur.execute("SELECT periodo, resultado_json FROM historico_analise_bp WHERE id = %s AND (entidade_id = %s OR entidade_id IS NULL)", (id, ent_id))
        else:
            cur.execute("SELECT periodo, resultado_json FROM historico_analise_bp WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"erro": True, "mensagem": "Nao encontrado"}
        dados = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        return {"erro": False, "periodo": row[0], "dados": dados}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.get("/historico")
def get_historico_bp(request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        ent_id = resolver_entidade_id(request, conn=conn)
        if ent_id is not None:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp WHERE entidade_id = %s ORDER BY id DESC", (ent_id,))
        else:
            cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_bp ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "periodo": r[1], "data_geracao": str(r[2])} for r in rows]
    except Exception as e:
        print(f"[BP] Erro ao listar historico: {e}")
        return []


@router.get("/{periodo}")
def api_analise_bp(periodo: str, request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        try:
            cur = conn.cursor()
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    "SELECT resultado_json FROM historico_analise_bp WHERE (periodo = %s OR periodo LIKE %s) AND (entidade_id = %s OR entidade_id IS NULL) ORDER BY id DESC LIMIT 1",
                    (periodo, f"{periodo}%", ent_id),
                )
            else:
                cur.execute(
                    "SELECT resultado_json FROM historico_analise_bp WHERE periodo = %s OR periodo LIKE %s ORDER BY id DESC LIMIT 1",
                    (periodo, f"{periodo}%"),
                )
            row = cur.fetchone()
            if not row or not row[0]:
                return {"erro": "faltando", "mensagem": f"Analise de BP nao encontrada no PostgreSQL para {periodo}"}
            rj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            return {"erro": False, "fonte": "postgresql", "dados": rj}
        finally:
            conn.close()
    except Exception as e:
        print(f"[BP] ERRO: {e}\n{traceback.format_exc()}")
        return {"erro": "interno", "mensagem": str(e)}


@router.post("/salvar/{periodo}/{periodo_anterior}")
def salvar_analise_bp(periodo: str, periodo_anterior: str, request: Request = None):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        try:
            cur = conn.cursor()
            periodo_label = f"{periodo} vs {periodo_anterior}"
            cur.execute(
                "SELECT resultado_json FROM historico_analise_bp WHERE periodo = %s OR periodo LIKE %s ORDER BY id DESC LIMIT 1",
                (periodo_label, f"{periodo}%"),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return {"ok": False, "mensagem": f"Dados de BP nao encontrados no PostgreSQL para {periodo}"}
            dados_json = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                "INSERT INTO historico_analise_bp (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, NOW(), %s, %s) RETURNING id",
                (periodo_label, json.dumps(dados_json, ensure_ascii=False), ent_id),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"ok": True, "id": new_id, "mensagem": "Salvo com sucesso"}
        finally:
            conn.close()
    except Exception as e:
        print(f"[BP] Erro ao salvar: {e}\n{traceback.format_exc()}")
        return {"ok": False, "mensagem": str(e)}


@router.delete("/excluir/{id}")
def excluir_bp(id: int):
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM historico_analise_bp WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}


@router.get("/gerar_pdf/{id}")
def gerar_pdf_analise_bp(id: int):
    try:
        from playwright.sync_api import sync_playwright
        import time
        
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT periodo, resultado_json FROM historico_analise_bp WHERE id = %s", (id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return Response(content=b"Registro nao encontrado", media_type="text/plain", status_code=404)
        
        url = "http://127.0.0.1:994/analise_bp?id=" + str(id) + "&_t=" + str(int(time.time()))
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            # Clicar no botao "Verificar Dados" para carregar os valores
            try:
                page.click("button:has-text('Verificar Dados')", timeout=5000)
                page.wait_for_timeout(3000)
            except Exception as e_click:
                print(f"[BP] AVISO: nao foi possivel clicar em Verificar Dados: {e_click}")
            # Esconder botoes/controles antes do PDF
            page.add_style_tag(content="button, select, .top-bar, .filtros, .sidebar { display: none !important; }")
            page.wait_for_timeout(1000)
            pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"})
            browser.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Analise_BP_{id}.pdf"},
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[BP] ERRO NO PDF: {e}\n{tb}")
        return Response(content=f"ERRO: {e}\n\n{tb}".encode("utf-8"), media_type="text/plain", status_code=500)
