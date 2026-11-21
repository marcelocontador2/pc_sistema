from pc_backend.app.config import PG_CONFIG
import psycopg2
# -*- coding: utf-8 -*-
"""
Rotas de Análise de Liquidez.
Extraído do main.py para refatoração.
"""

import os
import json
import datetime
from fastapi import APIRouter, Response, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
from fastapi.responses import FileResponse

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

# =========================================================
# FUNÇÃO AUXILIAR
# =========================================================
def _calc_liquidez(periodo, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    """Busca indices de liquidez/estrutura diretamente do PostgreSQL."""
    if not periodo:
        return None
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT resultado_json FROM historico_liquidez WHERE (periodo = %s) AND (%s IS NULL OR entidade_id = %s) ORDER BY id DESC LIMIT 1",
            (periodo, __ent_id, __ent_id),
        )
        row = cur.fetchone()
        if not row or not row[0]:
            return None
        rj = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        if not isinstance(rj, dict):
            return None
        valores = rj.get("valores") if isinstance(rj.get("valores"), dict) else {}
        return {
            "periodo": rj.get("periodo", periodo),
            "periodo_anterior": rj.get("periodo_anterior", ""),
            "liquidez": rj.get("liquidez", {}),
            "estrutura": rj.get("estrutura", {}),
            "valores": valores,
            "b_atual": valores.get("atual", {}),
            "b_ant": valores.get("anterior", {}),
        }
    finally:
        conn.close()


@router.get("/liquidez")
async def serve_liquidez(request: Request = None):
    caminho = os.path.join(FRONTEND_DIR, "liquidez.html")
    return FileResponse(caminho)


@router.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str, request: Request = None):
    dados = _calc_liquidez(periodo, request)
    if not dados:
        return {"erro": True, "mensagem": "Balanço Patrimonial não encontrado para este periodo."}
    return dados


@router.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez_rota(periodo: str, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    try:
        dados = _calc_liquidez(periodo, request)
        if not dados:
            return {"erro": True, "mensagem": "Sem dados para salvar."}
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
            id SERIAL PRIMARY KEY, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
                    (periodo, data_agora, json.dumps(dados, ensure_ascii=False), __ent_id))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Liquidez salva com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@router.get("/historico_liquidez")
def listar_historico_liquidez(request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_liquidez WHERE (%s IS NULL OR entidade_id = %s) ORDER BY id DESC", (__ent_id, __ent_id))
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


@router.get("/historico_liquidez/{id}")
async def get_liquidez_id(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = %s", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    dados = json.loads(row[2])
    dados["_periodo_hist"] = row[0]
    dados["_data_hist"] = row[1]
    return dados


@router.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_liquidez WHERE (id = %s) AND (%s IS NULL OR entidade_id = %s)", (id, __ent_id, __ent_id))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/gerar_pdf_liquidez/{id}")
def gerar_pdf_liquidez(id: int, request: Request = None):
    return Response(content="PDF em desenvolvimento", media_type="text/plain")