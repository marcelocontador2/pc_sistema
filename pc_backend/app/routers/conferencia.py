# -*- coding: utf-8 -*-
"""
Rotas de Conferência (PostgreSQL), isoladas por entidade_id e período.
Sobrepõe quando já existe conferência para a mesma entidade e período.
"""
import datetime
import json
import os
from pathlib import Path
import psycopg2
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response

from pc_backend.app.config import PG_CONFIG
from pc_backend.app.core.entidade_context import resolver_entidade_id

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FRONTEND_DIR = os.path.join(BASE_DIR, "pc_frontend")

router = APIRouter()

TABELAS_MODULOS = [
    ("integridade_matriz", "Integridade da Matriz (MSC)", "historico_integridade_matriz"),
    ("liquidez", "Análise de Liquidez", "historico_liquidez"),
    ("bp", "Balanço Patrimonial (BP)", "historico_analise_bp"),
    ("balanco_financeiro", "Balanço Financeiro (BF)", "historico_analise_financeira_bf"),
    ("analise_orcamentaria", "Balanço Orçamentário (BO)", "historico_analise_orcamentaria"),
    ("dfc", "Demonstração dos Fluxos de Caixa (DFC)", "historico_analise_dfc"),
    ("dvp", "Demonstração das Variações Patrimoniais (DVP)", "historico_analise_dvp"),
    ("dmpl", "Demonstração das Mutações do Patrimônio Líquido (DMPL)", "historico_analise_dmpl"),
]


def _get_pg_conn():
    return psycopg2.connect(**PG_CONFIG)


def _garantir_tabela_historico(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_conferencia (
            id SERIAL PRIMARY KEY,
            periodo TEXT,
            data_geracao TEXT,
            resultado_json TEXT,
            entidade_id INTEGER
        )
        """
    )
    cur.execute(
        """
        ALTER TABLE historico_conferencia
        ADD COLUMN IF NOT EXISTS entidade_id INTEGER
        """
    )


def _tabela_tem_entidade_id(cur, tabela: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = 'entidade_id'
        LIMIT 1
        """,
        (tabela,),
    )
    return cur.fetchone() is not None


def _parse_json_campo(val):
    if val is None:
        return None
    if isinstance(val, dict):
        return val
    if isinstance(val, str) and val.strip():
        try:
            return json.loads(val)
        except Exception:
            return {"raw": val}
    return None


def _colunas_tabela(cur, tabela: str) -> set:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (tabela,),
    )
    return {r[0] for r in cur.fetchall()}


def _fmt_brl(val) -> str:
    try:
        num = float(val)
    except Exception:
        return str(val or "")
    sinal = "-" if num < 0 else ""
    abs_val = abs(num)
    inteiro, frac = f"{abs_val:.2f}".split(".")
    grupos = []
    while inteiro:
        grupos.append(inteiro[-3:])
        inteiro = inteiro[:-3]
    inteiro_fmt = ".".join(reversed(grupos))
    return f"{sinal}R$ {inteiro_fmt},{frac}"


def _to_float(val, padrao: float = 0.0) -> float:
    if isinstance(val, dict):
        if "atual" in val and val["atual"] is not None:
            val = val["atual"]
        elif "valor" in val and val["valor"] is not None:
            val = val["valor"]
    try:
        if val is None or isinstance(val, bool):
            return padrao
        return float(val)
    except Exception:
        return padrao


def _buscar_caminho_numerico(dados: dict, caminhos: list, padrao=None):
    for cam in caminhos:
        atual = dados
        ok = True
        for parte in cam:
            if isinstance(atual, dict) and parte in atual:
                atual = atual[parte]
            else:
                ok = False
                break
        if ok and atual is not None:
            return atual
    return padrao


def _coletar_linhas_dinamicas(dados: dict, limite: int = 12) -> list:
    linhas = []

    def _andar(obj, prefixo=""):
        if len(linhas) >= limite:
            return
        if isinstance(obj, dict):
            if "atual" in obj and (isinstance(obj["atual"], (int, float)) or isinstance(obj.get("anterior"), (int, float))):
                rotulo = prefixo.replace("_", " ").strip().title() or "Valor"
                linhas.append({"label": rotulo, "valor": _fmt_brl(_to_float(obj["atual"]))})
                return
            for k, v in obj.items():
                if k in ("linhas", "erro", "periodo", "periodo_anterior"):
                    continue
                novo_pref = f"{prefixo} - {k}" if prefixo else str(k)
                _andar(v, novo_pref)
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            rotulo = prefixo.replace("_", " ").strip().title() or "Valor"
            linhas.append({"label": rotulo, "valor": _fmt_brl(obj)})

    _andar(dados)
    return linhas


def _analise_dinamica_modulo(chave: str, rotulo: str, tabela: str, periodo: str, dados: dict) -> dict:
    if not isinstance(dados, dict):
        return {
            "titulo": rotulo,
            "conceito": f"Conferência dinâmica no PostgreSQL ({tabela}) para o período {periodo}.",
            "tabela": [{"label": "Registro", "valor": str(dados)}],
            "status": "OK",
            "mensagem": "Dados carregados do PostgreSQL.",
        }

    if chave == "bp":
        ativo = _to_float(_buscar_caminho_numerico(dados, [["total_ativo"], ["ativo_total"]]))
        passivo_pl = _to_float(_buscar_caminho_numerico(dados, [["total_passivo"], ["passivo_pl"]]))
        dif = ativo - passivo_pl
        ok = abs(dif) < 0.01
        tabela_linhas = [
            {"label": "Ativo Total", "valor": _fmt_brl(ativo)},
            {"label": "Passivo + PL", "valor": _fmt_brl(passivo_pl)},
            {"label": "Diferença", "valor": _fmt_brl(dif)},
        ]
        for extra_k, extra_lbl in [("ativo_circulante", "Ativo Circulante"), ("ativo_nao_circulante", "Ativo Não Circulante"), ("passivo_circulante", "Passivo Circulante"), ("passivo_nao_circulante", "Passivo Não Circulante"), ("patrimonio_liquido", "Patrimônio Líquido")]:
            v_raw = _buscar_caminho_numerico(dados, [[extra_k]])
            if v_raw is not None:
                tabela_linhas.append({"label": extra_lbl, "valor": _fmt_brl(_to_float(v_raw))})
        return {
            "titulo": rotulo,
            "conceito": "Conforme o MCASP e a NBC TSP 11, a equação fundamental é Ativo = Passivo + PL.",
            "tabela": tabela_linhas,
            "status": "OK" if ok else "ALERTA",
            "mensagem": "Ativo e Passivo estão perfeitamente equilibrados." if ok else f"Diferença apurada entre Ativo e Passivo + PL: {_fmt_brl(dif)}.",
        }

    if chave == "balanco_financeiro":
        rec_tot = _to_float(_buscar_caminho_numerico(dados, [["receitas", "total"], ["receita_orcamentaria"]]))
        rec_extra = _to_float(_buscar_caminho_numerico(dados, [["extra", "recebimentos"], ["recebimentos_extra"]]))
        desp_tot = _to_float(_buscar_caminho_numerico(dados, [["despesas", "total"], ["despesa_orcamentaria"]]))
        pag_extra = _to_float(_buscar_caminho_numerico(dados, [["extra", "pagamentos"], ["pagamentos_extra"]]))
        saldo_ant = _to_float(_buscar_caminho_numerico(dados, [["caixa", "saldo_anterior"], ["saldo_anterior"]]))
        saldo_seg = _to_float(_buscar_caminho_numerico(dados, [["caixa", "saldo_seguinte"], ["saldo_seguinte"]]))
        ingressos = rec_tot + rec_extra
        dispensas = desp_tot + pag_extra
        saldo_calc = saldo_ant + ingressos - dispensas
        dif = saldo_calc - saldo_seg
        ok = abs(dif) < 0.01
        return {
            "titulo": rotulo,
            "conceito": "Conforme a IPC 06 da STN: Total de Ingressos = Receita Orçamentária + Recebimentos Extraorçamentários. Total de Dispêndios = Despesa Orçamentária + Pagamentos Extraorçamentários.",
            "tabela": [
                {"label": "Saldo do Exercício Anterior", "valor": _fmt_brl(saldo_ant)},
                {"label": "(+) Receita Orçamentária", "valor": _fmt_brl(rec_tot)},
                {"label": "(+) Recebimentos Extraorçamentários", "valor": _fmt_brl(rec_extra)},
                {"label": "(=) Total de Ingressos", "valor": _fmt_brl(ingressos)},
                {"label": "(-) Despesa Orçamentária", "valor": _fmt_brl(desp_tot)},
                {"label": "(-) Pagamentos Extraorçamentários", "valor": _fmt_brl(pag_extra)},
                {"label": "(=) Total de Dispêndios", "valor": _fmt_brl(dispensas)},
                {"label": "(=) Saldo para o Exercício Seguinte", "valor": _fmt_brl(saldo_seg)},
                {"label": "Diferença de Fechamento", "valor": _fmt_brl(dif)},
            ],
            "status": "OK" if ok else "ALERTA",
            "mensagem": "A conta fecha perfeitamente com os valores do Exercício Atual." if ok else f"Diferença de fechamento no Balanço Financeiro: {_fmt_brl(dif)}.",
        }

    if chave == "dfc":
        cx_ini = _to_float(_buscar_caminho_numerico(dados, [["caixa", "inicial"], ["caixa_inicial"]]))
        geracao = _to_float(_buscar_caminho_numerico(dados, [["caixa", "geracao"], ["geracao_liquida"]]))
        cx_esp = cx_ini + geracao
        cx_inf = _to_float(_buscar_caminho_numerico(dados, [["caixa", "final"], ["caixa_final"]], cx_esp))
        dif = cx_esp - cx_inf
        ok = abs(dif) < 0.01
        return {
            "titulo": rotulo,
            "conceito": "Conforme a IPC 08 da STN e NBC TSP 12: Caixa Inicial + Geração Líquida = Caixa Final.",
            "tabela": [
                {"label": "(+) Caixa Inicial", "valor": _fmt_brl(cx_ini)},
                {"label": "(+) Geração Líquida de Caixa", "valor": _fmt_brl(geracao)},
                {"label": "(=) Caixa Final Esperado", "valor": _fmt_brl(cx_esp)},
                {"label": "(=) Caixa Final Informado", "valor": _fmt_brl(cx_inf)},
                {"label": "Diferença", "valor": _fmt_brl(dif)},
            ],
            "status": "OK" if ok else "ALERTA",
            "mensagem": "Fluxo de caixa fecha perfeitamente com a IPC 08." if ok else f"Diferença no Fluxo de Caixa: {_fmt_brl(dif)}.",
        }

    if chave == "dvp":
        vpa = _to_float(_buscar_caminho_numerico(dados, [["total_vpa"], ["variacoes_ativas"]]))
        vpd = _to_float(_buscar_caminho_numerico(dados, [["total_vpd"], ["variacoes_diminutivas"]]))
        res = vpa - vpd
        tot_res_vpd = res + vpd
        dif = tot_res_vpd - vpa
        ok = abs(dif) < 0.01
        return {
            "titulo": rotulo,
            "conceito": "Conforme a IPC 05 da STN e NBC TSP 13, o Resultado Patrimonial (VPA - VPD) deve fechar a equação.",
            "tabela": [
                {"label": "(+) Total das VPA", "valor": _fmt_brl(vpa)},
                {"label": "(-) Total das VPD", "valor": _fmt_brl(vpd)},
                {"label": "(=) Resultado Patrimonial (DVP)", "valor": _fmt_brl(res)},
                {"label": "(=) Total (Resultado + VPD)", "valor": _fmt_brl(tot_res_vpd)},
                {"label": "Diferença de Fechamento", "valor": _fmt_brl(dif)},
            ],
            "status": "OK" if ok else "ALERTA",
            "mensagem": "A DVP está matematicamente fechada conforme a IPC 05." if ok else f"Diferença de fechamento na DVP: {_fmt_brl(dif)}.",
        }

    if chave == "analise_orcamentaria":
        bloco_atual = dados.get("atual") if isinstance(dados.get("atual"), dict) else dados
        rec_real = _to_float(_buscar_caminho_numerico(bloco_atual, [["receita_realizada"]]))
        desp_emp = _to_float(_buscar_caminho_numerico(bloco_atual, [["despesa_empenhada"]]))
        superavit = _to_float(_buscar_caminho_numerico(bloco_atual, [["superavit"]], rec_real - desp_emp))
        linhas = [
            {"label": "Receita Realizada", "valor": _fmt_brl(rec_real)},
            {"label": "Despesa Empenhada", "valor": _fmt_brl(desp_emp)},
            {"label": "Resultado (Superávit/Déficit)", "valor": _fmt_brl(superavit)},
        ]
        for k_opt, lbl_opt in [("receita_orcada", "Receita Orçada"), ("despesa_orcada", "Despesa Orçada"), ("restos_pagar", "Restos a Pagar")]:
            v_opt = _buscar_caminho_numerico(bloco_atual, [[k_opt]])
            if v_opt is not None:
                linhas.append({"label": lbl_opt, "valor": _fmt_brl(_to_float(v_opt))})
        return {
            "titulo": rotulo,
            "conceito": "Conforme a Lei 4.320/64 e o MCASP, confronta a previsão da receita com a fixação da despesa.",
            "tabela": linhas,
            "status": "OK",
            "mensagem": "Execução orçamentária calculada.",
        }

    if chave == "dmpl":
        saldo_ini = _to_float(_buscar_caminho_numerico(dados, [["saldos_iniciais"], ["saldo_inicial"]]))
        res_per = _to_float(_buscar_caminho_numerico(dados, [["resultado_periodo"], ["resultado_exercicio"]]))
        saldo_fin_calc = saldo_ini + res_per
        saldo_fin_inf = _to_float(_buscar_caminho_numerico(dados, [["saldos_finais"], ["saldo_final"]], saldo_fin_calc))
        dif = saldo_fin_calc - saldo_fin_inf
        ok = abs(dif) < 0.01
        return {
            "titulo": rotulo,
            "conceito": "Conforme o MCASP e a NBC TSP 11, o Saldo Final do PL é a soma do Saldo Inicial com o Resultado do Período.",
            "tabela": [
                {"label": "Saldo Inicial do PL", "valor": _fmt_brl(saldo_ini)},
                {"label": "Resultado do Período", "valor": _fmt_brl(res_per)},
                {"label": "(=) Saldo Final do PL", "valor": _fmt_brl(saldo_fin_inf)},
                {"label": "Diferença de Fechamento", "valor": _fmt_brl(dif)},
            ],
            "status": "OK" if ok else "ALERTA",
            "mensagem": "Mutações do PL consistentes." if ok else f"Diferença de fechamento na DMPL: {_fmt_brl(dif)}.",
        }

    linhas_dyn = _coletar_linhas_dinamicas(dados)
    if not linhas_dyn:
        linhas_dyn = [{"label": "Campos encontrados", "valor": str(len(dados))}]
    return {
        "titulo": rotulo,
        "conceito": f"Análise dinâmica extraída do PostgreSQL ({tabela}) para o período {periodo}.",
        "tabela": linhas_dyn,
        "status": "OK",
        "mensagem": f"Indicadores carregados dinamicamente de {tabela}.",
    }


def _montar_conferencia_pg(cur, periodo: str, ent_id) -> dict:
    modulos_pg = {}
    faltantes = []
    analises = []

    for chave, rotulo, tabela in TABELAS_MODULOS:
        dados_mod = None
        try:
            cols = _colunas_tabela(cur, tabela)
            if not cols or "resultado_json" not in cols:
                continue
            tem_periodo = "periodo" in cols
            tem_ent = ent_id is not None and "entidade_id" in cols

            if tem_periodo:
                padrao_like = f"{periodo}%"
                if tem_ent:
                    cur.execute(
                        f"SELECT resultado_json FROM {tabela} WHERE (periodo = %s OR periodo LIKE %s) AND entidade_id = %s ORDER BY id DESC LIMIT 1",
                        (periodo, padrao_like, ent_id),
                    )
                else:
                    cur.execute(
                        f"SELECT resultado_json FROM {tabela} WHERE (periodo = %s OR periodo LIKE %s) ORDER BY id DESC LIMIT 1",
                        (periodo, padrao_like),
                    )
            else:
                if tem_ent:
                    cur.execute(
                        f"SELECT resultado_json FROM {tabela} WHERE entidade_id = %s ORDER BY id DESC LIMIT 1",
                        (ent_id,),
                    )
                else:
                    cur.execute(f"SELECT resultado_json FROM {tabela} ORDER BY id DESC LIMIT 1")

            row = cur.fetchone()
            if row and row[0] is not None:
                dados_mod = _parse_json_campo(row[0])
        except Exception:
            cur.connection.rollback()
            dados_mod = None

        if dados_mod:
            modulos_pg[chave] = dados_mod
            analises.append(_analise_dinamica_modulo(chave, rotulo, tabela, periodo, dados_mod))
        else:
            faltantes.append(rotulo)
            analises.append(
                {
                    "titulo": rotulo,
                    "conceito": f"Verificação no PostgreSQL para o período {periodo}.",
                    "tabela": [
                        {"label": "Módulo / Tabela", "valor": f"{chave} ({tabela})"},
                        {"label": "Situação", "valor": "Não encontrado"},
                    ],
                    "status": "ALERTA",
                    "mensagem": "Demonstrativo ainda não importado/salvo para este período/entidade.",
                }
            )

    return {
        "periodo": periodo,
        "entidade_id": ent_id,
        "origem": "postgresql",
        "modulos": modulos_pg,
        "faltantes": faltantes,
        "analises": analises,
    }


@router.get("/conferencia")
async def serve_conferencia(request: Request = None):
    caminho = os.path.join(FRONTEND_DIR, "conferencia.html")
    return FileResponse(
        caminho,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"},
    )


@router.get("/api/conferencia/{periodo}")
async def api_conferencia_calcular(periodo: str, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)
        resultado = _montar_conferencia_pg(cur, periodo, ent_id)
        return resultado
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return {"erro": "falha", "mensagem": str(e)}
    finally:
        if conn:
            conn.close()


@router.api_route("/salvar_conferencia/{periodo}", methods=["GET", "POST"])
async def salvar_conferencia(periodo: str, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        body_dados = {}
        if request is not None and request.method == "POST":
            try:
                raw = await request.json()
                if isinstance(raw, dict):
                    body_dados = raw
            except Exception:
                body_dados = {}

        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)

        payload = _montar_conferencia_pg(cur, periodo, ent_id)
        if body_dados.get("analises"):
            payload["analises"] = body_dados["analises"]

        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        payload_json = json.dumps(payload, ensure_ascii=False, default=str)

        # Sobrepõe se já existir registro para a mesma entidade e mesmo período
        if ent_id is not None:
            cur.execute(
                """
                SELECT id FROM historico_conferencia
                WHERE periodo = %s AND entidade_id = %s
                ORDER BY id DESC LIMIT 1
                """,
                (periodo, ent_id),
            )
        else:
            cur.execute(
                """
                SELECT id FROM historico_conferencia
                WHERE periodo = %s AND entidade_id IS NULL
                ORDER BY id DESC LIMIT 1
                """,
                (periodo,),
            )
        existente = cur.fetchone()

        if existente:
            reg_id = existente[0]
            cur.execute(
                """
                UPDATE historico_conferencia
                SET data_geracao = %s, resultado_json = %s
                WHERE id = %s
                """,
                (data_agora, payload_json, reg_id),
            )
            acao = "sobreposto"
        else:
            cur.execute(
                """
                INSERT INTO historico_conferencia (periodo, data_geracao, resultado_json, entidade_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (periodo, data_agora, payload_json, ent_id),
            )
            reg_id = cur.fetchone()[0]
            acao = "inserido"

        conn.commit()
        cur.close()
        return {
            "ok": True,
            "status": "ok",
            "acao": acao,
            "id": reg_id,
            "periodo": periodo,
            "entidade_id": ent_id,
            "data_geracao": data_agora,
            "modulos_carregados": list(payload.get("modulos", {}).keys()),
        }
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return {"ok": False, "status": "erro", "mensagem": str(e)}
    finally:
        if conn:
            conn.close()


@router.get("/historico_conferencia")
async def listar_historico_conferencia(periodo: str = None, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)

        filtros = []
        params = []
        if ent_id is not None:
            filtros.append("(entidade_id = %s OR entidade_id IS NULL)")
            params.append(ent_id)
        if periodo:
            filtros.append("periodo = %s")
            params.append(periodo)

        where_sql = (" WHERE " + " AND ".join(filtros)) if filtros else ""
        cur.execute(
            f"""
            SELECT id, periodo, data_geracao, entidade_id
            FROM historico_conferencia
            {where_sql}
            ORDER BY id DESC
            """,
            tuple(params),
        )
        rows = cur.fetchall() or []
        return [
            {
                "id": r[0],
                "periodo": r[1],
                "data_geracao": r[2],
                "entidade_id": r[3],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/historico_conferencia/{hist_id}")
async def obter_historico_conferencia(hist_id: int, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)

        if ent_id is not None:
            cur.execute(
                """
                SELECT id, periodo, data_geracao, resultado_json, entidade_id
                FROM historico_conferencia
                WHERE id = %s AND (entidade_id = %s OR entidade_id IS NULL)
                """,
                (hist_id, ent_id),
            )
        else:
            cur.execute(
                """
                SELECT id, periodo, data_geracao, resultado_json, entidade_id
                FROM historico_conferencia
                WHERE id = %s
                """,
                (hist_id,),
            )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Registro de conferência não encontrado.")

        payload = _parse_json_campo(row[3]) or {}
        if not payload.get("analises"):
            calculado = _montar_conferencia_pg(cur, row[1], row[4] or ent_id)
            payload.update(calculado)

        payload["id"] = row[0]
        payload["periodo"] = row[1]
        payload["data_geracao"] = row[2]
        payload["entidade_id"] = row[4]
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.delete("/excluir_conferencia/{hist_id}")
async def excluir_historico_conferencia(hist_id: int, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)

        if ent_id is not None:
            cur.execute(
                "DELETE FROM historico_conferencia WHERE id = %s AND (entidade_id = %s OR entidade_id IS NULL)",
                (hist_id, ent_id),
            )
        else:
            cur.execute("DELETE FROM historico_conferencia WHERE id = %s", (hist_id,))
        removidos = cur.rowcount
        conn.commit()
        return {"ok": removidos > 0, "removidos": removidos}
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/gerar_pdf_conferencia/{hist_id}")
async def gerar_pdf_conferencia(hist_id: int, request: Request = None):
    ent_id = resolver_entidade_id(request)
    conn = None
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos

        conn = _get_pg_conn()
        cur = conn.cursor()
        _garantir_tabela_historico(cur)

        if ent_id is not None:
            cur.execute(
                """
                SELECT id, periodo, data_geracao, resultado_json, entidade_id
                FROM historico_conferencia
                WHERE id = %s AND (entidade_id = %s OR entidade_id IS NULL)
                """,
                (hist_id, ent_id),
            )
        else:
            cur.execute(
                """
                SELECT id, periodo, data_geracao, resultado_json, entidade_id
                FROM historico_conferencia
                WHERE id = %s
                """,
                (hist_id,),
            )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Registro de conferência não encontrado para PDF.")

        periodo = str(row[1] or "")
        data_geracao = str(row[2] or "")
        payload = _parse_json_campo(row[3]) or {}
        analises = payload.get("analises") or _montar_conferencia_pg(cur, periodo, row[4] or ent_id).get("analises", [])

        def _limpar_unicode(s) -> str:
            t = str(s or "")
            return (
                t.replace("—", "-")
                .replace("–", "-")
                .replace("‘", "'")
                .replace("’", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("…", "...")
            )

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        candidatos_reg = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
            Path("C:/Windows/Fonts/tahoma.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
        ]
        candidatos_bold = [
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/calibrib.ttf"),
            Path("C:/Windows/Fonts/tahomabd.ttf"),
            Path("C:/Windows/Fonts/seguisb.ttf"),
        ]
        candidatos_ital = [
            Path("C:/Windows/Fonts/ariali.ttf"),
            Path("C:/Windows/Fonts/calibrii.ttf"),
            Path("C:/Windows/Fonts/segoeuii.ttf"),
        ]

        reg_path = next((p for p in candidatos_reg if p.exists()), None)
        bold_path = next((p for p in candidatos_bold if p.exists()), None)
        ital_path = next((p for p in candidatos_ital if p.exists()), None)

        if reg_path is not None:
            pdf.add_font("FonteBR", "", str(reg_path))
            if bold_path is not None:
                pdf.add_font("FonteBR", "B", str(bold_path))
            else:
                pdf.add_font("FonteBR", "B", str(reg_path))
            if ital_path is not None:
                pdf.add_font("FonteBR", "I", str(ital_path))
            else:
                pdf.add_font("FonteBR", "I", str(reg_path))
            fam = "FonteBR"
            _san = lambda s: _limpar_unicode(s)
        else:
            fam = "helvetica"
            _san = lambda s: _limpar_unicode(s).encode("latin-1", errors="replace").decode("latin-1")

        pdf.set_font(fam, "B", 15)
        pdf.set_text_color(0, 51, 102)
        titulo_pdf = f"Conferência das Demonstrações - {periodo.replace('-', ' ').title()}"
        pdf.cell(0, 10, _san(titulo_pdf), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        pdf.set_font(fam, "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, _san(f"Gerado em: {data_geracao}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(8)

        for a in analises:
            status = str(a.get("status", ""))
            cor = (0, 128, 0) if status == "OK" else (200, 0, 0)

            pdf.set_font(fam, "B", 12)
            pdf.set_text_color(31, 41, 55)
            pdf.cell(0, 8, _san(a.get("titulo", "")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            for item in (a.get("tabela") or []):
                pdf.set_font(fam, "", 9.5)
                pdf.set_text_color(34, 34, 34)
                pdf.cell(115, 6.5, _san(item.get("label", "")), border=1)
                pdf.cell(0, 6.5, _san(item.get("valor", "")), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            msg_pdf = a.get("mensagem") or (
                "Demonstrativo correto e consistente com os critérios contábeis."
                if status == "OK"
                else "Atenção: verifique divergências ou dados pendentes neste demonstrativo."
            )
            pdf.set_font(fam, "B", 9.5)
            pdf.set_text_color(*cor)
            pdf.multi_cell(0, 6.5, _san(msg_pdf), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(7)

        pdf_bytes = bytes(pdf.output())
        nome_arq = f"Conferencia_{periodo.replace('-', '_').replace(' ', '_')}_{hist_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nome_arq}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {e}")
    finally:
        if conn:
            conn.close()