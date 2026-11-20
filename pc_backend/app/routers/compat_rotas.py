import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, Request

from pc_backend.app.config import PG_CONFIG
from pc_backend.app.core.entidade_context import resolver_entidade_id

router = APIRouter(tags=["compatibilidade_postgresql"])


def _garantir_tabelas_compat(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notas_mcasp_modelo (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(50),
            nivel VARCHAR(50),
            titulo TEXT,
            texto TEXT,
            ordem INTEGER DEFAULT 0,
            entidade_id BIGINT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_centro_custos (
            id SERIAL PRIMARY KEY,
            periodo VARCHAR(100),
            data_geracao VARCHAR(60),
            dados_json TEXT,
            entidade_id BIGINT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS relatorio_v2_salvo (
            id SERIAL PRIMARY KEY,
            periodo VARCHAR(100),
            texto_total TEXT,
            texto_concentracao TEXT,
            texto_alertas TEXT,
            texto_recomendacoes TEXT,
            data_edicao VARCHAR(60),
            entidade_id BIGINT
        )
        """
    )


def _listar_historico_json_pg(tabela: str, request: Request, col_json: str = "resultado_json"):
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                """,
                (tabela,),
            )
            cols = {r[0] for r in cur.fetchall()}
            if not cols:
                return []

            json_expr = col_json if col_json in cols else ("dados_json" if "dados_json" in cols else "NULL::text")
            data_expr = "data_geracao" if "data_geracao" in cols else "NULL::text"

            if "entidade_id" in cols and ent_id is not None:
                cur.execute(
                    f"SELECT id, periodo, {data_expr}, {json_expr} FROM {tabela} WHERE entidade_id = %s ORDER BY id DESC",
                    (ent_id,),
                )
            else:
                cur.execute(f"SELECT id, periodo, {data_expr}, {json_expr} FROM {tabela} ORDER BY id DESC")
            rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "periodo": r[1],
                "data_geracao": str(r[2]) if r[2] is not None else "",
                "dados": r[3],
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        conn.close()


@router.get("/api/notas_mcasp")
def api_get_notas_mcasp(request: Request):
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            _garantir_tabelas_compat(cur)
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'notas_mcasp_modelo'
                """
            )
            cols = {r["column_name"] for r in cur.fetchall()}
            order_col = "ordem" if "ordem" in cols else "id"
            if "entidade_id" in cols and ent_id is not None:
                cur.execute(
                    f"SELECT * FROM notas_mcasp_modelo WHERE entidade_id = %s OR entidade_id IS NULL ORDER BY {order_col} ASC, id ASC",
                    (ent_id,),
                )
            else:
                cur.execute(f"SELECT * FROM notas_mcasp_modelo ORDER BY {order_col} ASC, id ASC")
            rows = cur.fetchall()
        conn.commit()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


@router.post("/api/notas_mcasp/salvar")
async def api_salvar_notas_mcasp(request: Request):
    body = await request.json()
    itens = body.get("itens", [])
    if not itens:
        return {"ok": False, "mensagem": "Nenhum item enviado"}

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            _garantir_tabelas_compat(cur)
            for item in itens:
                if "id" in item:
                    cur.execute(
                        "UPDATE notas_mcasp_modelo SET texto = %s WHERE id = %s",
                        (item.get("texto", ""), item["id"]),
                    )
        conn.commit()
        return {"ok": True, "atualizados": len(itens)}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()


@router.post("/api/notas_mcasp/gerar_auto")
async def api_gerar_auto_mcasp(request: Request):
    itens = api_get_notas_mcasp(request)
    return {"ok": True, "itens": itens, "total": len(itens)}


@router.get("/historico_analise_patrimonial")
def get_historico_analise_patrimonial(request: Request):
    return _listar_historico_json_pg("historico_analise_patrimonial", request, "resultado_json")


@router.get("/historico_composicao_receitas_despesas")
def get_historico_composicao_receitas_despesas(request: Request):
    return _listar_historico_json_pg("historico_composicao_receitas_despesas", request, "resultado_json")


@router.get("/historico_panorama")
def get_historico_panorama(request: Request):
    return _listar_historico_json_pg("historico_panorama", request, "resultado_json")


@router.get("/historico_centro_custos")
def get_historico_centro_custos(request: Request):
    return _listar_historico_json_pg("historico_centro_custos", request, "dados_json")


@router.post("/salvar_centro_custos")
async def salvar_centro_custos(request: Request):
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}), ensure_ascii=False)
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            _garantir_tabelas_compat(cur)
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                """
                INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json, entidade_id)
                VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (periodo, data_geracao, dados_json, ent_id),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return {"ok": True, "id": new_id}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()


@router.post("/excluir_multiplos_centro_custos")
async def excluir_multiplos_centro_custos(request: Request):
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            _garantir_tabelas_compat(cur)
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    "DELETE FROM historico_centro_custos WHERE id = ANY(%s) AND entidade_id = %s",
                    (ids, ent_id),
                )
            else:
                cur.execute("DELETE FROM historico_centro_custos WHERE id = ANY(%s)", (ids,))
            excluidos = cur.rowcount
        conn.commit()
        return {"ok": True, "excluidos": excluidos}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()


@router.post("/salvar_relatorio_v2")
async def salvar_relatorio_v2(request: Request):
    dados = await request.json()
    periodo = dados.get("periodo")
    texto_total = dados.get("texto_total")
    texto_concentracao = dados.get("texto_concentracao")
    texto_alertas = dados.get("texto_alertas")
    texto_recomendacoes = dados.get("texto_recomendacoes")
    data_edicao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            _garantir_tabelas_compat(cur)
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                """
                INSERT INTO relatorio_v2_salvo
                    (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao, entidade_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (
                    periodo,
                    texto_total,
                    texto_concentracao,
                    texto_alertas,
                    texto_recomendacoes,
                    data_edicao,
                    ent_id,
                ),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return {"ok": True, "id": new_id}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()


@router.get("/historico_custo_pessoal")
def get_historico_custo_pessoal(request: Request):
    return _listar_historico_json_pg("historico_custo_pessoal", request, "resultado_json")


@router.post("/excluir_multiplos_custo_pessoal")
async def excluir_multiplos_custo_pessoal(request: Request):
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    "DELETE FROM historico_custo_pessoal WHERE id = ANY(%s) AND entidade_id = %s",
                    (ids, ent_id),
                )
            else:
                cur.execute("DELETE FROM historico_custo_pessoal WHERE id = ANY(%s)", (ids,))
            excluidos = cur.rowcount
        conn.commit()
        return {"ok": True, "excluidos": excluidos}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()


@router.get("/historico_conferencia")
def get_historico_conferencia(request: Request):
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            for tabela in ("historico_conferencia", "conferencia_historico", "historico_conferencia_demonstracoes"):
                cur.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    """,
                    (tabela,),
                )
                cols = {r[0] for r in cur.fetchall()}
                if not cols:
                    continue
                json_col = "resultado_json" if "resultado_json" in cols else ("dados_json" if "dados_json" in cols else "NULL::text")
                data_col = "data_geracao" if "data_geracao" in cols else ("criado_em" if "criado_em" in cols else "NULL::text")
                if "entidade_id" in cols and ent_id is not None:
                    cur.execute(
                        f"SELECT id, periodo, {data_col}, {json_col} FROM {tabela} WHERE entidade_id = %s ORDER BY id DESC",
                        (ent_id,),
                    )
                else:
                    cur.execute(f"SELECT id, periodo, {data_col}, {json_col} FROM {tabela} ORDER BY id DESC")
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "periodo": r[1],
                        "data_geracao": str(r[2]) if r[2] is not None else "",
                        "dados": r[3],
                    }
                    for r in rows
                ]
        return []
    except Exception:
        return []
    finally:
        conn.close()


# --- Rotas de exclusao adicionadas para padronizacao entre modulos ---
def _executar_delete_historico(tabela: str, item_id: int, request: Request = None):
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = None
            try:
                ent_id = resolver_entidade_id(request, conn=conn) if request is not None else None
            except TypeError:
                try:
                    ent_id = resolver_entidade_id(request) if request is not None else None
                except Exception:
                    ent_id = None
            except Exception:
                ent_id = None

            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s AND column_name = 'entidade_id'",
                (tabela,),
            )
            tem_entidade = cur.fetchone() is not None

            if tem_entidade and ent_id is not None:
                cur.execute(f"DELETE FROM {tabela} WHERE id = %s AND entidade_id = %s", (item_id, ent_id))
            else:
                cur.execute(f"DELETE FROM {tabela} WHERE id = %s", (item_id,))
            removidos = cur.rowcount
        conn.commit()
        return {"ok": True, "removidos": removidos, "excluido": removidos > 0}
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        return {"ok": False, "mensagem": str(exc)}
    finally:
        try:
            conn.close()
        except Exception:
            pass

@router.delete("/excluir_conferencia/{item_id}")
@router.delete("/api/excluir_conferencia/{item_id}")
async def excluir_conferencia_item(item_id: int, request: Request = None):
    for tab in ("historico_conferencia", "historico_conferencia_demonstracoes", "historico_conferencias", "conferencia_historico"):
        res = _executar_delete_historico(tab, item_id, request)
        if res.get("ok") and res.get("removidos", 0) > 0:
            return res
    return _executar_delete_historico("historico_conferencia", item_id, request)

@router.delete("/excluir_custo_pessoal/{item_id}")
@router.delete("/api/excluir_custo_pessoal/{item_id}")
async def excluir_custo_pessoal_item(item_id: int, request: Request = None):
    return _executar_delete_historico("historico_custo_pessoal", item_id, request)

@router.delete("/excluir_analise_patrimonial/{item_id}")
@router.delete("/api/analise_patrimonial/excluir/{item_id}")
async def excluir_analise_patrimonial_item(item_id: int, request: Request = None):
    for tab in ("historico_analise_patrimonial", "historico_analise_dvp", "historico_analise_bp"):
        res = _executar_delete_historico(tab, item_id, request)
        if res.get("ok") and res.get("removidos", 0) > 0:
            return res
    return _executar_delete_historico("historico_analise_patrimonial", item_id, request)
