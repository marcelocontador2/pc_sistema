# -*- coding: utf-8 -*-
"""
Rotas de Conferência.
Extraído do main.py para refatoração.
"""
import os
import json
import datetime
import sqlite3
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
DB_PATH = os.path.join(BASE_DIR, "pc_storage", "banco_dados.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

# =========================================================
# ROTAS
# =========================================================

@router.get("/conferencia")
async def serve_conferencia():
    from fastapi.responses import FileResponse
    caminho = os.path.join(FRONTEND_DIR, "conferencia.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})

@router.get("/api/conferencia/{periodo}")
async def api_conferencia_calcular(periodo: str):
    try:
        from .matriz_integridade import _get_csv
        pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
        faltando = [p for p in pecas_obrigatorias if not _get_csv(p, periodo)]
        if faltando:
            return {"erro": "faltando", "pecas": faltando}
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        return dados
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}

@router.get("/salvar_conferencia/{periodo}")
async def salvar_conferencia(periodo: str):
    try:
        from integridade import analise_integridade
        dados = await analise_integridade(periodo)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_conferencia (

            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_conferencia (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados)))
        conn.commit()
        conn.close()
        return {"mensagem": "Conferencia salva!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historico_conferencia")
def listar_conferencia():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_conferencia ORDER BY id DESC")
    rows = cursor.fetchall()
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

@router.get("/historico_conferencia/{id}")
async def buscar_conferencia(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT resultado_json FROM historico_conferencia WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Nao encontrado")
    return json.loads(row[0])

@router.delete("/excluir_conferencia/{id}")
async def excluir_conferencia(id: int):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_conferencia WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Excluido"}
# =======================================================
# ROTAS ISOLADAS: INTEGRIDADE (Tabela historico_integridade_matriz)
# =======================================================

@router.get("/gerar_pdf_conferencia/{id}")
async def gerar_pdf_conferencia(id: int):
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        import sqlite3, json, os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_conferencia WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row: raise HTTPException(status_code=404, detail="Historico nao encontrado")
        periodo, data_geracao, json_str = row
        dados = json.loads(json_str)
        analises = dados.get("analises", [])
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, f"Conferencia das Demonstracoes - {periodo.replace('-', ' ').title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        for a in analises:
            cor = (0, 128, 0) if a["status"] == "OK" else (255, 0, 0)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 8, a["titulo"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, a["conceito"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            for item in a["tabela"]:
                pdf.cell(100, 6, item["label"], border=1)
                pdf.cell(0, 6, item["valor"], border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(*cor)
            pdf.multi_cell(0, 6, a["mensagem"], border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(8)
        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Conferencia_{periodo.replace('-', '_')}.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# PDF da Integridade (Tabela historico_integridade_matriz)
async def api_analise_orcamentaria_bo(periodo: str):
    try:
        # === REGRA DE INTEGRIDADE ===
        from .matriz_integridade import _get_csv
        caminho_check = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho_check or not os.path.exists(caminho_check):
            return {"erro": "faltando", "pecas": ["Balanço Orçamentário"]}
        from .matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
        caminho = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        if not caminho or not os.path.exists(caminho):
            return {"erro": True, "mensagem": f"BO do perí­odo {periodo} não foi importado."}
        linhas = _ler_linhas(caminho)
        def buscar(termo, col, apos=0):
            for i, p in enumerate(linhas):
                if i < apos or not p: continue
                if termo.upper() in p[0].strip().upper() and len(p) > col:
                    return abs(_limpar_valor(p[col]))
            return 0.0
        receita = buscar("SUB-TOTAL DAS RECEITAS", 6)
        receita_orc = buscar("SUB-TOTAL DAS RECEITAS", 5)
        empenhada = buscar("SUB-TOTAL DAS DESPESAS", 4)
        despesa_orc = buscar("SUB-TOTAL DAS DESPESAS", 3)
        idx_desp = next((i for i, p in enumerate(linhas) if p and "SUB-TOTAL DAS DESPESAS" in p[0].upper()), 0)
        restos = buscar("TOTAL:", 6, apos=idx_desp)
        return {
            "erro": False,
            "receita_realizada": receita,
            "despesa_empenhada": empenhada,
            "superavit": receita - empenhada,
            "restos_pagar": restos,
            "receita_orcada": receita_orc,
            "despesa_orcada": despesa_orc,
            "pct_receita": round(receita / receita_orc * 100, 2) if receita_orc else 0,
            "pct_despesa": round(empenhada / despesa_orc * 100, 2) if despesa_orc else 0,
        }
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

