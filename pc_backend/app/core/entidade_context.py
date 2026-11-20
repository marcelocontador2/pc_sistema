from typing import Optional
from fastapi import Request
import psycopg2
from psycopg2.extras import RealDictCursor
from pc_backend.app.config import PG_CONFIG


def obter_cofen_id(conn) -> Optional[int]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id FROM configuracoes_entidade
            WHERE UPPER(COALESCE(nome_fantasia, '')) = 'COFEN'
               OR razao_social ILIKE '%Conselho Federal de Enfermagem%'
            ORDER BY id ASC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row:
            return int(row["id"])
        cur.execute("SELECT id FROM configuracoes_entidade ORDER BY id ASC LIMIT 1")
        row2 = cur.fetchone()
        return int(row2["id"]) if row2 else None


def resolver_entidade_id(request: Optional[Request], conn=None, entidade_solicitada: Optional[int] = None) -> Optional[int]:
    fecha_conn = False
    if conn is None:
        conn = psycopg2.connect(**PG_CONFIG)
        fecha_conn = True

    try:
        usuario_id_hdr = None
        entidade_hdr = None
        if request is not None:
            raw_uid = request.headers.get("x-usuario-id") or request.headers.get("X-Usuario-Id")
            raw_eid = request.headers.get("x-entidade-id") or request.headers.get("X-Entidade-Id")
            if raw_uid and str(raw_uid).strip().isdigit():
                usuario_id_hdr = int(str(raw_uid).strip())
            if raw_eid and str(raw_eid).strip().isdigit():
                entidade_hdr = int(str(raw_eid).strip())

        if usuario_id_hdr is not None:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, perfil, entidade_id FROM usuarios WHERE id = %s AND COALESCE(ativo, TRUE) = TRUE",
                    (usuario_id_hdr,),
                )
                u = cur.fetchone()
            if u:
                if u["entidade_id"] is not None:
                    return int(u["entidade_id"])
                if str(u["perfil"] or "").lower() in ("admin", "administrador"):
                    if entidade_solicitada is not None:
                        return int(entidade_solicitada)
                    if entidade_hdr is not None:
                        return int(entidade_hdr)

        if entidade_solicitada is not None:
            return int(entidade_solicitada)
        if entidade_hdr is not None:
            return int(entidade_hdr)

        return obter_cofen_id(conn)
    finally:
        if fecha_conn:
            conn.close()
