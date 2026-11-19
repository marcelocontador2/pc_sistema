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
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()

        tabelas_historico = [
            ("integridade_matriz", "historico_integridade_matriz"),
            ("liquidez", "historico_liquidez"),
            ("bp", "historico_analise_bp"),
            ("balanco_financeiro", "historico_balanco_financeiro"),
            ("analise_orcamentaria", "historico_analise_orcamentaria"),
            ("dfc", "historico_dfc"),
            ("dvp", "historico_dvp"),
            ("dmpl", "historico_dmpl"),
        ]

        modulos_pg = {}
        for chave, tabela in tabelas_historico:
            try:
                cur.execute(
                    f"SELECT resultado_json FROM {tabela} WHERE periodo = %s ORDER BY id DESC LIMIT 1",
                    (periodo,),
                )
                row = cur.fetchone()
                if row and row[0] is not None:
                    modulos_pg[chave] = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            except Exception:
                conn.rollback()

        contas_mem = carregar_contas_memoria("conferencia", periodo)
        payload = {
            "periodo": periodo,
            "origem": "postgresql",
            "modulos": modulos_pg,
            "contas_memoria_count": len(contas_mem) if isinstance(contas_mem, (list, dict)) else 0,
        }

        cur.execute("""
            CREATE TABLE IF NOT EXISTS historico_conferencia (
                id SERIAL PRIMARY KEY,
                periodo TEXT,
                data_geracao TEXT,
                resultado_json TEXT
            )
        """)
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute(
            "INSERT INTO historico_conferencia (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
            (periodo, data_agora, json.dumps(payload, ensure_ascii=False, default=str)),
        )
        conn.commit()
        cur.close()
        return {"status": "ok", "periodo": periodo, "data_geracao": data_agora, "modulos_carregados": list(modulos_pg.keys())}
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return {"status": "erro", "mensagem": str(e)}
    finally:
        if conn:
            conn.close()
