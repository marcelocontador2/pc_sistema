import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG
from pc_backend.app.core.entidade_context import resolver_entidade_id

router = APIRouter(tags=["notas_explicativas"])


def _get_conn():
    return psycopg2.connect(**PG_CONFIG)


def _garantir_tabela(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS historico_notas_explicativas (
                id BIGSERIAL PRIMARY KEY,
                periodo TEXT NOT NULL,
                data_geracao TEXT,
                resultado_json TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        cur.execute("ALTER TABLE historico_notas_explicativas ADD COLUMN IF NOT EXISTS data_geracao TEXT")
        cur.execute("ALTER TABLE historico_notas_explicativas ADD COLUMN IF NOT EXISTS resultado_json TEXT")
        cur.execute("ALTER TABLE historico_notas_explicativas ADD COLUMN IF NOT EXISTS entidade_id BIGINT")


def _serializar_row(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("resultado_json")
    if raw is None:
        raw = row.get("dados") or "{}"
    if isinstance(raw, dict):
        dados = raw
    else:
        try:
            dados = json.loads(raw) if raw else {}
        except Exception:
            dados = {}
    if not isinstance(dados, dict):
        dados = {}

    dt = row.get("data_geracao")
    if hasattr(dt, "strftime"):
        data_str = dt.strftime("%d/%m/%Y %H:%M")
    else:
        data_str = str(dt or "")

    return {
        "id": row["id"],
        "periodo": row["periodo"],
        "dados": dados,
        "resultado_json": json.dumps(dados, ensure_ascii=False),
        "data_geracao": data_str,
    }


@router.get("/historico_notas_explicativas")
def listar_historico_notas(request: Request):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        ent_id = resolver_entidade_id(request, conn=conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if ent_id is not None:
                cur.execute(
                    """
                    SELECT id, periodo, data_geracao, resultado_json
                    FROM historico_notas_explicativas
                    WHERE entidade_id = %s
                    ORDER BY id DESC
                    """,
                    (ent_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT id, periodo, data_geracao, resultado_json
                    FROM historico_notas_explicativas
                    ORDER BY id DESC
                    """
                )
            rows = cur.fetchall()
        return [_serializar_row(dict(r)) for r in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.get("/historico_notas_explicativas/{item_id}")
def obter_historico_nota(item_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, periodo, data_geracao, resultado_json FROM historico_notas_explicativas WHERE id = %s",
                (item_id,),
            )
            row = cur.fetchone()
        if not row:
            return {"erro": "Registro de hist?rico n?o encontrado."}
        return _serializar_row(dict(row))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.get("/api/notas_explicativas/{periodo}")
def carregar_notas_periodo(periodo: str, request: Request):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        ent_id = resolver_entidade_id(request, conn=conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if ent_id is not None:
                cur.execute(
                    """
                    SELECT id, periodo, data_geracao, resultado_json
                    FROM historico_notas_explicativas
                    WHERE periodo = %s AND entidade_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (periodo, ent_id),
                )
            else:
                cur.execute(
                    """
                    SELECT id, periodo, data_geracao, resultado_json
                    FROM historico_notas_explicativas
                    WHERE periodo = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (periodo,),
                )
            row = cur.fetchone()
        if row:
            ser = _serializar_row(dict(row))
            return {
                "ok": True,
                "id": ser["id"],
                "periodo": ser["periodo"],
                "notas": ser["dados"].get("notas", []),
                "observacoes": ser["dados"].get("observacoes", ""),
                "conclusao": ser["dados"].get("conclusao", ""),
                "dados": ser["dados"],
            }
        return {
            "ok": True,
            "id": None,
            "periodo": periodo,
            "notas": [],
            "observacoes": "",
            "conclusao": "",
            "dados": {"notas": [], "observacoes": "", "conclusao": ""},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.post("/salvar_notas_explicativas/{periodo}")
async def salvar_notas_periodo(periodo: str, request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}

    dados_payload = body.get("dados") if isinstance(body.get("dados"), dict) else {
        "notas": body.get("notas", []),
        "observacoes": body.get("observacoes", ""),
        "conclusao": body.get("conclusao", ""),
    }
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        ent_id = resolver_entidade_id(request, conn=conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO historico_notas_explicativas (periodo, data_geracao, resultado_json, entidade_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id, periodo, data_geracao, resultado_json
                """,
                (periodo, data_agora, json.dumps(dados_payload, ensure_ascii=False), ent_id),
            )
            row = cur.fetchone()
        conn.commit()
        ser = _serializar_row(dict(row))
        return {"ok": True, "id": ser["id"], "registro": ser}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.delete("/excluir_notas_explicativas/{item_id}")
def excluir_historico_nota(item_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM historico_notas_explicativas WHERE id = %s RETURNING id",
                (item_id,),
            )
            removido = cur.fetchone()
        if not removido:
            raise HTTPException(status_code=404, detail="Registro n?o encontrado.")
        conn.commit()
        return {"ok": True, "excluido_id": removido[0]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


def _atualizar_dados_registro(conn, relatorio_id: int, updater):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, periodo, data_geracao, resultado_json FROM historico_notas_explicativas WHERE id = %s",
            (relatorio_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Relat?rio de notas n?o encontrado.")
        ser = _serializar_row(dict(row))
        dados = dict(ser["dados"])
        notas = list(dados.get("notas") or [])
        updater(dados, notas)
        dados["notas"] = notas
        cur.execute(
            """
            UPDATE historico_notas_explicativas
            SET resultado_json = %s
            WHERE id = %s
            RETURNING id, periodo, data_geracao, resultado_json
            """,
            (json.dumps(dados, ensure_ascii=False), relatorio_id),
        )
        atualizado = cur.fetchone()
    conn.commit()
    return _serializar_row(dict(atualizado))


@router.post("/api/incluir_nota/{relatorio_id}")
async def incluir_nota(relatorio_id: int, request: Request):
    payload = await request.json()
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        def _add(dados, notas):
            notas.append(payload)
        res = _atualizar_dados_registro(conn, relatorio_id, _add)
        return {"ok": True, "registro": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.api_route("/api/editar_nota/{relatorio_id}/{index}", methods=["POST", "PUT"])
async def editar_nota(relatorio_id: int, index: int, request: Request):
    payload = await request.json()
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        def _edit(dados, notas):
            if index < 0 or index >= len(notas):
                raise HTTPException(status_code=404, detail="?ndice de nota inv?lido.")
            if isinstance(notas[index], dict) and isinstance(payload, dict):
                notas[index].update(payload)
            else:
                notas[index] = payload
        res = _atualizar_dados_registro(conn, relatorio_id, _edit)
        return {"ok": True, "registro": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.delete("/api/excluir_nota/{relatorio_id}/{index}")
def excluir_nota(relatorio_id: int, index: int):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        def _del(dados, notas):
            if index < 0 or index >= len(notas):
                raise HTTPException(status_code=404, detail="?ndice de nota inv?lido.")
            notas.pop(index)
        res = _atualizar_dados_registro(conn, relatorio_id, _del)
        return {"ok": True, "registro": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.post("/api/observacoes_notas/{relatorio_id}")
async def salvar_observacoes_notas(relatorio_id: int, request: Request):
    payload = await request.json()
    if isinstance(payload, dict):
        obs = payload.get("observacoes") if "observacoes" in payload else payload.get("texto", "")
        item = payload.get("item")
    else:
        obs = ""
        item = None
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        def _obs(dados, notas):
            dados["observacoes"] = obs
            if item is not None:
                obs_lista = list(dados.get("observacoes_itens") or [])
                obs_lista.append({"item": item, "texto": obs})
                dados["observacoes_itens"] = obs_lista
        res = _atualizar_dados_registro(conn, relatorio_id, _obs)
        return {"ok": True, "registro": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.get("/api/conclusao_notas/{relatorio_id}")
def obter_conclusao_notas(relatorio_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, periodo, data_geracao, resultado_json FROM historico_notas_explicativas WHERE id = %s",
                (relatorio_id,),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Relat?rio n?o encontrado.")
        ser = _serializar_row(dict(row))
        concl = ser["dados"].get("conclusao", "")
        return {"ok": True, "conclusao": concl, "texto": concl}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.post("/api/conclusao_notas/{relatorio_id}")
async def salvar_conclusao_notas(relatorio_id: int, request: Request):
    payload = await request.json()
    if isinstance(payload, dict):
        concl = payload.get("conclusao") if "conclusao" in payload else payload.get("texto", "")
    else:
        concl = ""
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        def _conc(dados, notas):
            dados["conclusao"] = concl
        res = _atualizar_dados_registro(conn, relatorio_id, _conc)
        return {"ok": True, "registro": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.get("/gerar_pdf_notas/{relatorio_id}")
def gerar_pdf_notas(relatorio_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, periodo, data_geracao, resultado_json FROM historico_notas_explicativas WHERE id = %s",
                (relatorio_id,),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Hist?rico n?o encontrado.")
        ser = _serializar_row(dict(row))
        linhas = [
            "NOTAS EXPLICATIVAS",
            f"Per?odo: {ser['periodo']}",
            f"Data de gera??o: {ser['data_geracao']}",
            "-" * 50,
        ]
        for idx, n in enumerate(ser["dados"].get("notas") or [], 1):
            if isinstance(n, dict):
                titulo = n.get("titulo") or n.get("item") or f"Nota {idx}"
                texto = n.get("texto") or n.get("descricao") or ""
                linhas.append(f"{idx}. {titulo}: {texto}")
            else:
                linhas.append(f"{idx}. {n}")
        if ser["dados"].get("observacoes"):
            linhas.extend(["", "Observa??es:", str(ser["dados"]["observacoes"])])
        if ser["dados"].get("conclusao"):
            linhas.extend(["", "Conclus?o:", str(ser["dados"]["conclusao"])])
        conteudo = "\n".join(linhas).encode("utf-8")
        return Response(
            content=conteudo,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'inline; filename="notas_explicativas_{relatorio_id}.txt"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


def _garantir_tabela_declaracao(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS declaracao_conformidade (
                id BIGSERIAL PRIMARY KEY,
                texto TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0
            )
            """
        )


@router.get("/api/declaracao_conformidade")
def listar_declaracao_conformidade():
    conn = _get_conn()
    try:
        _garantir_tabela_declaracao(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, texto, ordem FROM declaracao_conformidade ORDER BY ordem ASC, id ASC")
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.get("/api/declaracao_conformidade/{item_id}")
def obter_item_declaracao(item_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela_declaracao(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, texto, ordem FROM declaracao_conformidade WHERE id = %s", (item_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item n?o encontrado.")
        return dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.post("/api/declaracao_conformidade")
async def criar_item_declaracao(request: Request):
    payload = await request.json()
    texto = (payload.get("texto") or "").strip() if isinstance(payload, dict) else ""
    if not texto:
        raise HTTPException(status_code=400, detail="Texto obrigat?rio.")
    conn = _get_conn()
    try:
        _garantir_tabela_declaracao(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO declaracao_conformidade (texto, ordem)
                VALUES (%s, COALESCE((SELECT MAX(ordem) + 1 FROM declaracao_conformidade), 1))
                RETURNING id, texto, ordem
                """,
                (texto,),
            )
            row = cur.fetchone()
        conn.commit()
        return {"ok": True, "item": dict(row)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.api_route("/api/declaracao_conformidade/{item_id}", methods=["PUT", "POST"])
async def atualizar_item_declaracao(item_id: int, request: Request):
    payload = await request.json()
    texto = (payload.get("texto") or "").strip() if isinstance(payload, dict) else ""
    if not texto:
        raise HTTPException(status_code=400, detail="Texto obrigat?rio.")
    conn = _get_conn()
    try:
        _garantir_tabela_declaracao(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE declaracao_conformidade
                SET texto = %s
                WHERE id = %s
                RETURNING id, texto, ordem
                """,
                (texto, item_id),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item n?o encontrado.")
        conn.commit()
        return {"ok": True, "item": dict(row)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.delete("/api/declaracao_conformidade/{item_id}")
def excluir_item_declaracao(item_id: int):
    conn = _get_conn()
    try:
        _garantir_tabela_declaracao(conn)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM declaracao_conformidade WHERE id = %s RETURNING id", (item_id,))
            removido = cur.fetchone()
        if not removido:
            raise HTTPException(status_code=404, detail="Item n?o encontrado.")
        conn.commit()
        return {"ok": True, "excluido_id": removido[0]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()
