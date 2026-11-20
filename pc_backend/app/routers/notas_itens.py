"""
Endpoints REST para conclusoes, observacoes e comentarios por item, periodo e ano.
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request
from pc_backend.app.core.entidade_context import resolver_entidade_id
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG
from pc_backend.app.notas_periodo import (
    ITENS_PADRAO,
    garantir_tabela_notas,
    listar_notas_item,
    salvar_nota_item,
)

router = APIRouter(prefix="/api/notas_itens", tags=["notas_itens"])


class NotaItemPayload(BaseModel):
    item: str = Field(..., min_length=1, description="Ex.: '1. conferencia' ou '2. integridade'")
    item_numero: int | None = Field(default=None, ge=0)
    periodo: str = Field(..., min_length=1, description="Ex.: '2026-TRIMESTRE-3'")
    ano: int = Field(..., ge=2000, le=2100)
    tipo: str = Field(default="observacao", description="conclusao | observacao | comentario")
    texto: str = Field(..., min_length=1)
    metadados: dict[str, Any] | None = None


class NotaItemUpdatePayload(BaseModel):
    tipo: str | None = None
    texto: str | None = Field(default=None, min_length=1)
    metadados: dict[str, Any] | None = None


@router.get("/catalogo")
def catalogo_itens_notas(request: Request = None):
    return {"ok": True, "itens": ITENS_PADRAO}


@router.get("")
def get_notas_itens(
    item: str | None = Query(default=None),
    item_numero: int | None = Query(default=None),
    periodo: str | None = Query(default=None),
    ano: int | None = Query(default=None),
    tipo: str | None = Query(default=None),
):
    try:
        registros = listar_notas_item(
            item=item,
            item_numero=item_numero,
            periodo=periodo,
            ano=ano,
            tipo=tipo,
        )
        return {"ok": True, "total": len(registros), "registros": registros}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("")
def post_nota_item(payload: NotaItemPayload, request: Request = None):
    try:
        salvo = salvar_nota_item(
            item=payload.item,
            periodo=payload.periodo,
            ano=payload.ano,
            texto=payload.texto,
            tipo=payload.tipo,
            item_numero=payload.item_numero,
            metadados=payload.metadados,
        )
        return {"ok": True, "registro": salvo}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{nota_id}")
def put_nota_item(nota_id: int, payload: NotaItemUpdatePayload, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        garantir_tabela_notas(conn)
        campos: list[str] = []
        params: list[Any] = []
        if payload.tipo is not None:
            t = payload.tipo.strip().lower()
            if t not in ("conclusao", "observacao", "comentario"):
                t = "observacao"
            campos.append("tipo = %s")
            params.append(t)
        if payload.texto is not None:
            campos.append("texto = %s")
            params.append(payload.texto.strip())
        if payload.metadados is not None:
            import json
            campos.append("metadados = %s::jsonb")
            params.append(json.dumps(payload.metadados, ensure_ascii=False))
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo informado para atualizacao.")
        campos.append("registrado_em = NOW()")
        params.append(nota_id)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                UPDATE registro_conclusao_observacoes
                SET {', '.join(campos)}
                WHERE id = %s
                RETURNING id, item_numero, item, periodo, ano, tipo, texto, metadados, registrado_em
                """,
                params,
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Nota nao encontrada.")
        conn.commit()
        return {"ok": True, "registro": dict(row)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{nota_id}")
def delete_nota_item(nota_id: int, request: Request = None):
    __ent_id = resolver_entidade_id(request)
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        garantir_tabela_notas(conn)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM registro_conclusao_observacoes WHERE id = %s AND (%s IS NULL OR entidade_id = %s) RETURNING id", (nota_id, __ent_id, __ent_id))
            removido = cur.fetchone()
        if not removido:
            raise HTTPException(status_code=404, detail="Nota nao encontrada.")
        conn.commit()
        return {"ok": True, "excluido_id": removido[0]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()