from pc_backend.app.db_memoria import carregar_contas_memoria
# -*- coding: utf-8 -*-
"""
Rotas de Confer?ncia.
Extra?do do main.py para refatora??o (PostgreSQL).
"""
import os
import json
import datetime
import psycopg2
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import FileResponse

from pc_backend.app.config import PG_CONFIG

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()


def _get_pg_conn():
    return psycopg2.connect(**PG_CONFIG)


# =========================================================
# ROTAS
# =========================================================

@router.get("/conferencia")
async def serve_conferencia():
    caminho = os.path.join(FRONTEND_DIR, "conferencia.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"})


def _buscar_conferencia_pg(periodo: str) -> dict | None:
    if not periodo:
        return None
    conn = _get_pg_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT resultado_json FROM historico_conferencia WHERE periodo = %s ORDER BY id DESC LIMIT 1",
            (periodo,),
        )
        row = cur.fetchone()
        if not row or not row[0]:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    except Exception:
        return None
    finally:
        conn.close()


@router.get("/api/conferencia/{periodo}")
async def api_conferencia_calcular(periodo: str):
    try:
        dados = _buscar_conferencia_pg(periodo)
        if not dados:
            return {"erro": "faltando", "mensagem": f"Dados de confer?ncia do per?odo {periodo} n?o encontrados no PostgreSQL."}
        return dados
    except Exception as e:
        return {"erro": "falha", "mensagem": str(e)}


@router.get("/salvar_conferencia/{periodo}")
async def salvar_conferencia(periodo: str):
    try:
        from pc_backend.integridade import analise_integridade
        dados = await analise_integridade(periodo)
        conn = _get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_conferencia (
                id SERIAL PRIMARY KEY,
                periodo TEXT,
                data_geracao TEXT,
                resultado_json TEXT
            )
        """)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            "INSERT INTO historico_conferencia (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
            (periodo, data_agora, json.dumps(dados, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensagem": "Conferencia salva!", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historico_conferencia")
def listar_conferencia():
    conn = _get_pg_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_conferencia ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    resultado = []
    for r in rows:
        resultado.append({
            "id": r[0],
            "periodo": r[1],
            "data_geracao": r[2],
            "dados": r[3]
        })

    return Response(content=json.dumps(resultado, ensure_ascii=False), media_type="application/json")


@router.get("/historico_conferencia/{id}")
async def buscar_conferencia(id: int):
    conn = _get_pg_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT resultado_json FROM historico_conferencia WHERE id = %s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Nao encontrado")
    return row[0] if isinstance(row[0], dict) else json.loads(row[0])


@router.delete("/excluir_conferencia/{id}")
async def excluir_conferencia(id: int):
    conn = _get_pg_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_conferencia WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensagem": "Excluido"}


# =======================================================
# PDF DE CONFER?NCIA
# =======================================================

@router.get("/gerar_pdf_conferencia/{id}")
async def gerar_pdf_conferencia(id: int):
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos

        conn = _get_pg_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_conferencia WHERE id = %s", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Historico nao encontrado")

        periodo, data_geracao, json_str = row
        dados = json.loads(json_str) if isinstance(json_str, str) else (json_str or {})
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
            cor = (0, 128, 0) if a.get("status") == "OK" else (255, 0, 0)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 8, str(a.get("titulo", "")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, str(a.get("conceito", "")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            for item in a.get("tabela", []):
                pdf.cell(100, 6, str(item.get("label", "")), border=1)
                pdf.cell(0, 6, str(item.get("valor", "")), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(*cor)
            pdf.multi_cell(0, 6, str(a.get("mensagem", "")), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(8)

        pdf_bytes = pdf.output()
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Conferencia_{periodo.replace('-', '_')}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
