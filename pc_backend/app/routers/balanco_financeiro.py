"""
Rota do Balanco Financeiro - integrada ao PostgreSQL (historico_analise_financeira_bf)
com fallback opcional para CSV em uploads_raw.
"""
import csv
import json
import os
from fastapi import APIRouter, HTTPException, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
import psycopg2
from pc_backend.app.config import PG_CONFIG

router = APIRouter(prefix="/api/balanco_financeiro", tags=["balanco_financeiro"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "pc_storage", "uploads_raw")


def limpar(v, request: Request = None):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("R$", "").strip()
    if s in ["-", "0,00", ""]:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _buscar_no_banco(periodo: str, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, periodo, data_geracao, resultado_json
                FROM historico_analise_financeira_bf
                WHERE periodo = %s OR periodo LIKE %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (periodo, f"{periodo}%"),
            )
            row = cur.fetchone()
            if not row:
                return None
            _, per_salvo, dt_geracao, raw_json = row
            payload = json.loads(raw_json) if isinstance(raw_json, str) else (raw_json or {})
            return {
                "erro": False,
                "fonte": "postgresql",
                "historico_id": row[0],
                "periodo": per_salvo,
                "data_geracao": dt_geracao,
                "dados": payload,
            }
    finally:
        conn.close()


def processar_bf(caminho: str = "", periodo: str | None = None, request: Request = None):
    if periodo:
        res = buscar_bf_postgresql(periodo)
        if res:
            return res
    return {"erro": "faltando", "mensagem": "Dados do Balanco Financeiro nao encontrados no PostgreSQL."}


@router.get("/{periodo}")
async def api_balanco_financeiro_periodo(periodo: str, request: Request = None):
    try:
        res_db = _buscar_no_banco(periodo)
        if res_db is not None:
            return res_db
        return {"erro": "nao_encontrado", "origem": "postgresql", "periodo": periodo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))