from pc_backend.app.db_memoria import carregar_contas_memoria
import json
import psycopg2
from fastapi import HTTPException, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
from pc_backend.app.config import PG_CONFIG
# -*- coding: utf-8 -*-
"""
Rotas de Integridade (Matriz de Integridade).
Extraído do main.py para refatoração.
"""
import os
import datetime
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "pc_storage", "uploads_raw")
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")



router = APIRouter()

# =========================================================
# ROTAS
# =========================================================

@router.get("/historico_integridade")
async def listar_historico(request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        if __ent_id is not None:
            cursor.execute('''
                SELECT id, periodo, data_geracao FROM historico_integridade
                WHERE entidade_id = %s
                ORDER BY id DESC
            ''', (__ent_id,))
        else:
            cursor.execute('''
                SELECT id, periodo, data_geracao FROM historico_integridade
                ORDER BY id DESC
            ''')
        rows = cursor.fetchall()
        conn.close()
        historico = []
        for r in rows:
            historico.append({"id": r[0], "periodo": r[1], "data_geracao": r[2]})
        return historico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Rota que abre um histí³rico especifico pelo ID

@router.get("/historico_integridade/{id}")
async def buscar_historico(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        if __ent_id is not None:
            cursor.execute('''SELECT resultado_json FROM historico_integridade WHERE id = %s AND entidade_id = %s''', (id, __ent_id))
        else:
            cursor.execute('''SELECT resultado_json FROM historico_integridade WHERE id = %s''', (id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Historico nao encontrado")
        return json.loads(row[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integridade")
async def serve_integridade(request: Request = None):
    caminho = os.path.join(FRONTEND_DIR, "integridade.html")
    return FileResponse(caminho)

def _parse_json_pg(val, request: Request = None):
    if val is None:
        return None
    if isinstance(val, dict):
        return val
    try:
        return json.loads(val)
    except Exception:
        return None


def _buscar_integridade_matriz_pg(periodo: str, request: Request = None) -> dict | None:
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT resultado_json FROM historico_integridade_matriz WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 5",
            (periodo, __ent_id, __ent_id),
        )
        for (raw,) in cur.fetchall():
            rj = _parse_json_pg(raw)
            if isinstance(rj, dict) and rj.get("matriz"):
                return rj

        cur.execute(
            "SELECT resultado_json FROM historico_matriz_integridade WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 5",
            (periodo, __ent_id, __ent_id),
        )
        for (raw,) in cur.fetchall():
            rj = _parse_json_pg(raw)
            if isinstance(rj, dict) and rj.get("matriz"):
                return {
                    "periodo": periodo,
                    "matriz": rj.get("matriz", []),
                    "justificativas": rj.get("justificativas", {}),
                }

        cur.execute(
            "SELECT resultado_json FROM historico_integridade_matriz WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (periodo, __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if row and row[0]:
            rj = _parse_json_pg(row[0])
            if isinstance(rj, dict):
                return rj

        cur.execute(
            "SELECT resultado_json FROM historico_integridade WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (periodo, __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if row and row[0]:
            rj = _parse_json_pg(row[0])
            if isinstance(rj, dict):
                return rj

        return None
    finally:
        conn.close()


@router.get("/api/integridade_matriz/{periodo}")
async def api_integridade_matriz_calcular(periodo: str, request: Request = None):
    try:
        dados = _buscar_integridade_matriz_pg(periodo, request)
        if dados:
            return dados
        return {"erro": True, "mensagem": f"Dados de integridade n?o encontrados no PostgreSQL para {periodo}."}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.post("/api/integridade_matriz/{periodo}/salvar")
async def salvar_integridade_matriz(periodo: str, request: Request):
    __ent_id = resolver_entidade_id(request)
    from datetime import datetime
    
    # Definição local para garantir que a variável exista no escopo
        
    try:
        body = await request.json()
        matriz = body.get("matriz", [])
        justificativas = body.get("justificativas", {})
        
        dados_matriz = {
            "periodo": periodo,
            "matriz": matriz,
            "justificativas": justificativas
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Garante que a tabela exista no Postgres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
                id SERIAL PRIMARY KEY, 
                periodo TEXT, 
                data_geracao TEXT, 
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Matriz salva com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
    
    try:
        body = await request.json()
        matriz = body.get("matriz", [])
        justificativas = body.get("justificativas", {})
        
        dados_matriz = {
            "periodo": periodo,
            "matriz": matriz,
            "justificativas": justificativas
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Garante que a tabela exista no Postgres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
                id SERIAL PRIMARY KEY, 
                periodo TEXT, 
                data_geracao TEXT, 
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Matriz salva com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
        
        dados_matriz = {
            "periodo": periodo,
            "matriz": matriz,
            "justificativas": justificativas
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Cria a tabela se não existir no Postgres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
                id SERIAL PRIMARY KEY, 
                periodo TEXT, 
                data_geracao TEXT, 
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Matriz salva com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@router.get("/historico_integridade_matriz")
def listar_integridade_matriz(request: Request = None):
    __ent_id = resolver_entidade_id(request)
    
        
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_integridade_matriz WHERE (%s IS NULL OR entidade_id = %s) ORDER BY id DESC", (__ent_id, __ent_id))
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
        return resultado
    except Exception as e:
        return Response(content=json.dumps({"erro": True, "mensagem": str(e)}), media_type="application/json")
        return resultado
    except Exception as e:
        return Response(content=json.dumps({"erro": True, "mensagem": str(e)}), media_type="application/json")

@router.get("/historico_integridade_matriz/{id}")
async def buscar_integridade_matriz(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    
    # Definição local para garantir que a variável exista
        
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado_json FROM historico_integridade_matriz WHERE id = %s", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row: 
            raise HTTPException(status_code=404, detail="Não encontrado")
            
        return json.loads(row[0])
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@router.post("/excluir_multiplos_integridade_matriz")
async def excluir_integridade_matriz(request: Request):
    __ent_id = resolver_entidade_id(request)
    try:
        body = await request.json()
        ids = body.get("ids", [])
        if not ids:
            return {"ok": False, "mensagem": "Nenhum ID fornecido."}
            
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Formata os IDs para o IN do SQL
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM historico_integridade_matriz WHERE id IN ({placeholders})", tuple(ids))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensagem": "Excluído com sucesso!"}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}

@router.get("/gerar_pdf_integridade_matriz/{check_id}")
def gerar_pdf_integridade_matriz(check_id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    from fastapi.responses import Response
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    import psycopg2, json

    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_integridade_matriz WHERE id = %s", (check_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"erro": "Histórico não encontrado"}
        
        periodo, data_geracao, json_str = row
        dados = json.loads(json_str)
        matriz = dados.get("matriz", [])

        # Cria o PDF no formato Paisagem (Landscape) porque a tabela é larga
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # Cabeçalho
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, f"Matriz de Integridade - {periodo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Gerado em: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)

        # Larguras das colunas (Total ~ 267mm disponíveis no A4 Paisagem)
        w = [60, 26, 26, 26, 26, 26, 26, 26, 25]

        # Cabeçalho da Tabela
        pdf.set_font("helvetica", "B", 8)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        
        colunas = ["NOMENCLATURA", "BALANCETE", "BP", "BF", "BO", "DFC", "DVP", "DMPL", "CONF."]
        for i, col in enumerate(colunas):
            pdf.cell(w[i], 7, col, border=1, align="C", fill=True)
        pdf.ln()

        # Linhas da Tabela
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        
        for item in matriz:
            # Define cor da fonte da última coluna (CONF)
            conf = str(item.get("conf", ""))
            
            # Nomeclatura (com limite de tamanho para não quebrar)
            nome = str(item.get("item", ""))[:40]
            pdf.cell(w[0], 6, nome, border=1)
            
            # Demais colunas
            vals = [
                str(item.get("balancete", "-")),
                str(item.get("bp", "-")),
                str(item.get("bf", "-")),
                str(item.get("bo", "-")),
                str(item.get("dfc", "-")),
                str(item.get("dvp", "-")),
                str(item.get("dmpl", "-"))
            ]
            for i, v in enumerate(vals):
                pdf.cell(w[i+1], 6, v, border=1, align="R")
                
            # Coluna CONF (Colorida se for erro)
            if "OK" in conf:
                pdf.set_text_color(0, 128, 0) # Verde
            else:
                pdf.set_text_color(255, 0, 0) # Vermelho
            
            pdf.cell(w[8], 6, conf, border=1, align="C")
            pdf.set_text_color(0, 0, 0) # Reseta para preto
            pdf.ln()

        pdf_bytes = pdf.output()

        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=integridade_{periodo}.pdf"}
        )
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@router.get("/gerar_pdf_integridade/{id}")
def gerar_pdf_integridade_espelho(id: int, request: Request = None):
    return gerar_pdf_integridade_matriz(check_id=id)