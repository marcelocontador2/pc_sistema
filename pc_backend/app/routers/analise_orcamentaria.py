from pc_backend.app.db_memoria import salvar_contas_memoria, carregar_contas_memoria, _slug_conta
# -*- coding: utf-8 -*-
"""
Rotas de Análise Orçamentária.
Extraído do main.py para refatoração.
"""
import os
import json
import datetime
from fastapi import APIRouter, Request, Response, HTTPException
from pc_backend.app.core.entidade_context import resolver_entidade_id
from fastapi.responses import FileResponse, HTMLResponse
from pc_backend.app.config import PG_CONFIG
import psycopg2

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

# =========================================================
# ROTAS
# =========================================================

@router.get("/historico_analise_orcamentaria")
def get_historico_analise_orcamentaria(request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_analise_orcamentaria WHERE (%s IS NULL OR entidade_id = %s) ORDER BY id DESC", (__ent_id, __ent_id))
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

@router.get("/historico_analise_orcamentaria/{id}")
async def get_analise_orcamentaria_id(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT periodo, resultado_json FROM historico_analise_orcamentaria WHERE id=%s", (id,))
    row = cur.fetchone(); conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[1])

@router.post("/salvar_analise_orcamentaria/{periodo}")
async def salvar_analise_orcamentaria(periodo: str, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    atual = await api_analise_orcamentaria_bo(periodo)
    if atual.get("erro"):
        raise HTTPException(status_code=400, detail=atual.get("mensagem"))
    ano_anterior = str(int(periodo.split("-")[0]) - 1)
    periodo_anterior = periodo.replace(periodo.split("-")[0], ano_anterior, 1)
    anterior = await api_analise_orcamentaria_bo(periodo_anterior)
    dados = {"periodo_anterior": periodo_anterior, "periodo": periodo,
             "atual": atual, "anterior": anterior if not anterior.get("erro") else {}}
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_analise_orcamentaria (

        id SERIAL PRIMARY KEY, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("INSERT INTO historico_analise_orcamentaria (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
                (periodo, data_agora, json.dumps(dados)))
    conn.commit(); conn.close()
    return {"mensagem": "Salvo"}

@router.delete("/excluir_analise_orcamentaria/{id}")
async def excluir_analise_orcamentaria(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_analise_orcamentaria WHERE (id=%s) AND (%s IS NULL OR entidade_id = %s)", (id, __ent_id, __ent_id))
    conn.commit(); conn.close()
    return {"mensagem": "Excluido"}

@router.get("/gerar_pdf_analise_orcamentaria/{id}")
def gerar_pdf_analise_orcamentaria(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import io, tempfile, os, json
        import psycopg2
        from pc_backend.app.config import PG_CONFIG
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, resultado_json FROM historico_analise_orcamentaria WHERE id = %s", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, d_json = row
        d = json.loads(d_json)
        # Estrutura esperada: { atual: {...}, anterior: {...} }
        a = d.get("atual", {})
        b = d.get("anterior", {})
        # --- 1. GERA O GRíFICO (Atual primeiro) ---
        labels = ["Receita Realizada", "Despesa Empenhada", "Superavit"]
        ant = [b.get("receita_realizada", 0), b.get("despesa_empenhada", 0), b.get("superavit", 0)]
        atu = [a.get("receita_realizada", 0), a.get("despesa_empenhada", 0), a.get("superavit", 0)]
        fig, ax = plt.subplots(figsize=(6, 2.8), dpi=150)
        x = range(len(labels))
        # Atual (azul escuro) na esquerda, Anterior (azul claro) na direita
        ax.bar([i - 0.2 for i in x], atu, width=0.4, label="Atual", color="#003366")
        ax.bar([i + 0.2 for i in x], ant, width=0.4, label="Anterior", color="#4a90e2")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10)
        ax.legend(loc="upper right", fontsize=9, frameon=False)
        formatter = ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:,.1f} Mi")
        ax.yaxis.set_major_formatter(formatter)
        ax.tick_params(axis="y", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        img_path = os.path.join(tempfile.gettempdir(), f"grafico_orc_{id}.png")
        plt.savefig(img_path, bbox_inches="tight"); plt.close()
        # --- 2. MONTA O PDF ---
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold)
            f_family = "Arial"
        else:
            f_family = "helvetica"
        pdf.set_font(f_family, "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Analise Orcamentaria Comparativa", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font(f_family, "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Periodo de Referencia: {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(8)
        # Tabela: Indicador | Periodo Atual | Periodo Anterior | Var (%)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(f_family, "B", 10)
        pdf.cell(80, 8, "Indicador", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Periodo Atual", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Periodo Anterior", border=1, fill=True, align="C")
        pdf.cell(30, 8, "Var. (%)", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(f_family, "", 9)
        def fmt(v, request: Request = None): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # Indicadores na ordem que queremos
        # Calcula os percentuais na hora para garantir precisão
        rec_orc = a.get("receita_orcada", 0) or 0
        rec_real = a.get("receita_realizada", 0) or 0
        desp_orc = a.get("despesa_orcada", 0) or 0
        desp_emp = a.get("despesa_empenhada", 0) or 0

        rec_orc_ant = b.get("receita_orcada", 0) or 0
        rec_real_ant = b.get("receita_realizada", 0) or 0
        desp_orc_ant = b.get("despesa_orcada", 0) or 0
        desp_emp_ant = b.get("despesa_empenhada", 0) or 0

        pct_rec = (rec_real / rec_orc * 100) if rec_orc else 0
        pct_desp = (desp_emp / desp_orc * 100) if desp_orc else 0

        pct_rec_ant = (rec_real_ant / rec_orc_ant * 100) if rec_orc_ant else 0
        pct_desp_ant = (desp_emp_ant / desp_orc_ant * 100) if desp_orc_ant else 0

        ind = [
            ("Receita Realizada", rec_real, rec_real_ant, 1e6),
            ("Despesas Empenhadas", desp_emp, desp_emp_ant, 1e6),
            ("Superavit Orcamentario", a.get("superavit", 0), b.get("superavit", 0), 1e6),
            ("Restos a Pagar Inscritos", a.get("restos_pagar", 0), b.get("restos_pagar", 0), 1e6),
            ("Receitas Orcadas", rec_orc, rec_orc_ant, 1e6),
            ("Despesas Orcadas", desp_orc, desp_orc_ant, 1e6),
            ("% de Realizacao das Receitas", pct_rec, pct_rec_ant, 1),
            ("% de Realizacao das Despesas", pct_desp, pct_desp_ant, 1),
        ]

        for nome, va, vb, m in ind:
            var = ((va - vb) / abs(vb)) * 100 if vb != 0 else 0
            pdf.cell(80, 7, nome, border=1, align="L")
            pdf.cell(45, 7, fmt(va) if m == 1e6 else f"{va:.2f}%", border=1, align="R")
            pdf.cell(45, 7, fmt(vb) if m == 1e6 else f"{vb:.2f}%", border=1, align="R")
            if var >= 0: pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(220, 53, 69)
            pdf.cell(30, 7, f"{var:+.2f}%".replace(".", ","), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        # Grafico e Conclusao
        pdf.ln(8)
        y_atual = pdf.get_y()
        pdf.image(img_path, x=30, y=y_atual, w=110)
        # Conclusao no lado direito
        pdf.set_xy(150, y_atual)
        pdf.set_font(f_family, "B", 10)
        pdf.cell(0, 6, "Principais conclusoes:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(150)
        pdf.set_font(f_family, "", 8)
        txt_conclusao = f"A receita realizada representa {a.get('pct_receita', 0):.2f}% da previsao atualizada, enquanto as despesas empenhadas representam {a.get('pct_despesa', 0):.2f}% da dotacao atualizada."
        pdf.multi_cell(90, 4, txt_conclusao)
        pdf_bytes = bytes(pdf.output())
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=analise_orcamentaria_{id}.pdf"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analise_orcamentaria")
async def serve_analise_orcamentaria(request: Request = None):
    caminho = os.path.join(FRONTEND_DIR, "analise_orcamentaria.html")
    return FileResponse(caminho)



# === ROTA RESGATADA: CÁLCULO DO BALANÇO ORÇAMENTÁRIO ===
def _buscar_orcamentaria_pg(periodo_str: str, request: Request = None) -> dict | None:
    __ent_id = resolver_entidade_id(request)
    if not periodo_str:
        return None
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT resultado_json FROM historico_analise_orcamentaria WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (periodo_str, __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if row and row[0]:
            rj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            if isinstance(rj, dict):
                bloco = rj.get("atual") if isinstance(rj.get("atual"), dict) else rj
                if isinstance(bloco, dict) and ("receita_realizada" in bloco or "despesa_empenhada" in bloco):
                    out = dict(bloco)
                    out["erro"] = False
                    return out

        cur.execute(
            "SELECT resultado_json FROM historico_analise_orcamentaria WHERE (resultado_json LIKE %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (f'%"{periodo_str}"%', __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if row and row[0]:
            rj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            if isinstance(rj, dict):
                if rj.get("periodo") == periodo_str and isinstance(rj.get("atual"), dict):
                    out = dict(rj["atual"])
                    out["erro"] = False
                    return out
                if rj.get("periodo_anterior") == periodo_str and isinstance(rj.get("anterior"), dict):
                    out = dict(rj["anterior"])
                    out["erro"] = False
                    return out

        return None
    except Exception as e:
        print(f"[ORCAMENTARIA] Erro ao consultar PostgreSQL ({periodo_str}): {e}")
        return None
    finally:
        conn.close()


@router.get("/api/analise_orcamentaria_bo/{periodo}")
async def api_analise_orcamentaria_bo(periodo: str, request: Request = None):
    try:
        dados = _buscar_orcamentaria_pg(periodo)
        if not dados:
            return {"erro": True, "mensagem": f"Dados or?ament?rios do per?odo {periodo} n?o encontrados no PostgreSQL."}
        return dados
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}