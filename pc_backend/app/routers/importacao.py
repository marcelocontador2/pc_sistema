from pathlib import Path
import csv
import glob
import json
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from pc_backend.app.config import PG_CONFIG, UPLOADS_RAW
from pc_backend.app.core.entidade_context import resolver_entidade_id

router = APIRouter(tags=["importacao"])

_RAIZ = Path(__file__).resolve().parents[3]
_FRONTEND_DIR = _RAIZ / "pc_frontend"


def _extrair_tipo_e_periodo(nome_arquivo: str) -> tuple[str, str]:
    partes = nome_arquivo.replace(".csv", "").split("_")
    tipo = partes[0] if partes and partes[0] else "Desconhecido"
    periodo = "N?o identificado"
    for i, p in enumerate(partes):
        if len(p) == 4 and p.isdigit():
            if i + 2 < len(partes):
                periodo = f"{p} - {partes[i+1]} {partes[i+2]}"
            else:
                periodo = p
            break
    return tipo, periodo


@router.get("/importar", response_class=HTMLResponse)
@router.get("/importar.html", response_class=HTMLResponse)
def rota_importar():
    arq = _FRONTEND_DIR / "importar.html"
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="importar.html nao encontrado")


@router.get("/login", response_class=HTMLResponse)
@router.get("/login.html", response_class=HTMLResponse)
def rota_login():
    arq = _FRONTEND_DIR / "login.html"
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="login.html nao encontrado")


@router.get("/usuarios", response_class=HTMLResponse)
@router.get("/usuarios.html", response_class=HTMLResponse)
def rota_usuarios():
    arq = _FRONTEND_DIR / "usuarios.html"
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="usuarios.html nao encontrado")


@router.post("/upload")
async def upload_arquivo(
    request: Request,
    file: UploadFile = File(...),
    tipo_relatorio: str = Form(None),
    ano: str = Form(None),
    periodo_tipo: str = Form(None),
    periodo_valor: str = Form(None),
):
    Path(UPLOADS_RAW).mkdir(parents=True, exist_ok=True)
    nome_original = Path(file.filename or "arquivo.csv").name
    nome_arquivo = nome_original
    periodo_str = (
        f"{ano}_{periodo_tipo}_{periodo_valor}"
        if ano and periodo_tipo and periodo_valor
        else "2026_TRIMESTRE_3"
    )

    if tipo_relatorio:
        tipo = tipo_relatorio.upper()
        if "BALANCO_PATRIMONIAL" in tipo or tipo == "BP":
            nome_arquivo = f"BALANCO_PATRIMONIAL_{periodo_str}.csv"
        elif "BALANCETE" in tipo:
            nome_arquivo = f"BALANCETE_{periodo_str}.csv"
        elif "BALANCO_ORCAMENTARIO" in tipo:
            nome_arquivo = f"BALANCO_ORCAMENTARIO_{periodo_str}.csv"
        elif "BALANCO_FINANCEIRO" in tipo:
            nome_arquivo = f"BALANCO_FINANCEIRO_{periodo_str}.csv"
        elif "DFC" in tipo:
            nome_arquivo = f"DFC_{periodo_str}.csv"
        elif "DVP" in tipo:
            nome_arquivo = f"DVP_{periodo_str}.csv"
        elif "DMPL" in tipo:
            nome_arquivo = f"DMPL_{periodo_str}.csv"
        elif "CENTRO_CUSTOS" in tipo:
            nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
        elif "COMPARATIVO_RECEITAS" in tipo:
            nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"
        elif "COMPARATIVO_DESPESAS" in tipo:
            nome_arquivo = f"COMPARATIVO_DESPESAS_{periodo_str}.csv"

    caminho = Path(UPLOADS_RAW) / nome_arquivo
    conteudo = await file.read()
    with open(caminho, "wb") as f:
        f.write(conteudo)

    tipo_inf, periodo_inf = _extrair_tipo_e_periodo(nome_arquivo)
    if tipo_relatorio:
        tipo_inf = tipo_relatorio.upper()

    meta_json = json.dumps(
        {"tipo": tipo_inf, "periodo": periodo_inf, "caminho": str(caminho)},
        ensure_ascii=False,
    )

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            cur.execute(
                """
                INSERT INTO importacoes
                    (tipo_relatorio, ano, periodo_tipo, periodo_valor, nome_original, caminho_arquivo, data_importacao, entidade_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tipo_inf,
                    int(ano) if ano and ano.isdigit() else 2026,
                    periodo_tipo or "TRIMESTRE",
                    periodo_valor or "3",
                    nome_original,
                    str(caminho),
                    datetime.now().isoformat(),
                    ent_id,
                ),
            )
            if ent_id is not None:
                cur.execute(
                    "UPDATE arquivos_importados SET dados_json = %s WHERE nome_arquivo = %s AND entidade_id = %s",
                    (meta_json, nome_arquivo, ent_id),
                )
            else:
                cur.execute(
                    "UPDATE arquivos_importados SET dados_json = %s WHERE nome_arquivo = %s AND entidade_id IS NULL",
                    (meta_json, nome_arquivo),
                )
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO arquivos_importados (nome_arquivo, dados_json, entidade_id) VALUES (%s, %s, %s)",
                    (nome_arquivo, meta_json, ent_id),
                )

            # Grava/sobrepoe no PostgreSQL para que a conferencia encontre por entidade_id e periodo
            periodo_pg = (
                f"{ano}-{(periodo_tipo or 'TRIMESTRE').upper()}-{periodo_valor or '3'}"
                if (ano or periodo_tipo or periodo_valor)
                else "2026-TRIMESTRE-3"
            )
            mapa_hist = {
                "BALANCO_FINANCEIRO": "historico_analise_financeira_bf",
                "BF": "historico_analise_financeira_bf",
                "BALANCO_PATRIMONIAL": "historico_analise_bp",
                "BP": "historico_analise_bp",
                "BALANCO_ORCAMENTARIO": "historico_analise_orcamentaria",
                "BO": "historico_analise_orcamentaria",
                "DFC": "historico_analise_dfc",
                "DVP": "historico_analise_dvp",
                "DMPL": "historico_analise_dmpl",
            }
            tabela_hist = None
            for k, t_nome in mapa_hist.items():
                if k in (tipo_inf or "").upper():
                    tabela_hist = t_nome
                    break

            if tabela_hist:
                cur.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
                    (tabela_hist,),
                )
                if cur.fetchone():
                    cur.execute(
                        "SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name=%s AND column_name='entidade_id'",
                        (tabela_hist,),
                    )
                    tem_ent = cur.fetchone() is not None
                    dt_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    res_payload = json.dumps(
                        {
                            "origem": "importacao_pg",
                            "tipo": tipo_inf,
                            "periodo": periodo_pg,
                            "arquivo": nome_arquivo,
                            "tamanho_bytes": len(conteudo),
                        },
                        ensure_ascii=False,
                    )
                    if tem_ent and ent_id is not None:
                        cur.execute(
                            f"SELECT id FROM {tabela_hist} WHERE periodo = %s AND entidade_id = %s ORDER BY id DESC LIMIT 1",
                            (periodo_pg, ent_id),
                        )
                        exist_row = cur.fetchone()
                        if exist_row:
                            cur.execute(
                                f"UPDATE {tabela_hist} SET data_geracao = %s, resultado_json = %s WHERE id = %s",
                                (dt_str, res_payload, exist_row[0]),
                            )
                        else:
                            cur.execute(
                                f"INSERT INTO {tabela_hist} (periodo, data_geracao, resultado_json, entidade_id) VALUES (%s, %s, %s, %s)",
                                (periodo_pg, dt_str, res_payload, ent_id),
                            )
                    else:
                        cur.execute(
                            f"SELECT id FROM {tabela_hist} WHERE periodo = %s ORDER BY id DESC LIMIT 1",
                            (periodo_pg,),
                        )
                        exist_row = cur.fetchone()
                        if exist_row:
                            cur.execute(
                                f"UPDATE {tabela_hist} SET data_geracao = %s, resultado_json = %s WHERE id = %s",
                                (dt_str, res_payload, exist_row[0]),
                            )
                        else:
                            cur.execute(
                                f"INSERT INTO {tabela_hist} (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
                                (periodo_pg, dt_str, res_payload),
                            )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True, "mensagem": f"Arquivo {nome_arquivo} importado com sucesso!"}


@router.get("/api/relatorios_importados")
def api_relatorios_importados(request: Request):
    lista = []
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    """
                    SELECT nome_arquivo, dados_json
                    FROM arquivos_importados
                    WHERE entidade_id = %s
                    ORDER BY nome_arquivo ASC
                    """,
                    (ent_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT nome_arquivo, dados_json
                    FROM arquivos_importados
                    ORDER BY nome_arquivo ASC
                    """
                )
            rows = cur.fetchall()

            if not rows and ent_id in (None, 24):
                arquivos = glob.glob(os.path.join(str(UPLOADS_RAW), "*.csv"))
                for arq in sorted(arquivos):
                    if os.path.exists(arq):
                        nome = os.path.basename(arq)
                        tipo, periodo = _extrair_tipo_e_periodo(nome)
                        meta_json = json.dumps(
                            {"tipo": tipo, "periodo": periodo, "caminho": arq},
                            ensure_ascii=False,
                        )
                        cur.execute(
                            "INSERT INTO arquivos_importados (nome_arquivo, dados_json, entidade_id) VALUES (%s, %s, %s)",
                            (nome, meta_json, ent_id if ent_id is not None else 24),
                        )
                conn.commit()
                if ent_id is not None:
                    cur.execute(
                        "SELECT nome_arquivo, dados_json FROM arquivos_importados WHERE entidade_id = %s ORDER BY nome_arquivo ASC",
                        (ent_id,),
                    )
                else:
                    cur.execute("SELECT nome_arquivo, dados_json FROM arquivos_importados ORDER BY nome_arquivo ASC")
                rows = cur.fetchall()

        for r in rows:
            nome = r["nome_arquivo"]
            tipo_inf, periodo_inf = _extrair_tipo_e_periodo(nome)
            raw_json = r.get("dados_json")
            if raw_json:
                try:
                    info = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                    if isinstance(info, dict):
                        tipo_inf = info.get("tipo") or tipo_inf
                        periodo_inf = info.get("periodo") or periodo_inf
                except Exception:
                    pass
            lista.append({"nome": nome, "tipo": tipo_inf, "periodo": periodo_inf})
    finally:
        conn.close()

    return lista


@router.get("/api/ler_relatorio/{tipo}")
def ler_relatorio_csv(tipo: str, request: Request):
    conn = psycopg2.connect(**PG_CONFIG)
    arquivo = None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    """
                    SELECT nome_arquivo, dados_json
                    FROM arquivos_importados
                    WHERE entidade_id = %s AND nome_arquivo ILIKE %s
                    ORDER BY id DESC LIMIT 1
                    """,
                    (ent_id, f"%{tipo}%"),
                )
            else:
                cur.execute(
                    """
                    SELECT nome_arquivo, dados_json
                    FROM arquivos_importados
                    WHERE nome_arquivo ILIKE %s
                    ORDER BY id DESC LIMIT 1
                    """,
                    (f"%{tipo}%",),
                )
            reg = cur.fetchone()
            if reg:
                raw_json = reg.get("dados_json")
                if raw_json:
                    try:
                        info = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                        if isinstance(info, dict) and info.get("caminho") and os.path.exists(info["caminho"]):
                            arquivo = info["caminho"]
                    except Exception:
                        pass
                if not arquivo and reg.get("nome_arquivo"):
                    cand = Path(UPLOADS_RAW) / reg["nome_arquivo"]
                    if cand.exists():
                        arquivo = str(cand)
    finally:
        conn.close()

    if not arquivo:
        if ent_id is not None:
            return {"erro": f"Nenhum arquivo do tipo {tipo} importado para a entidade selecionada."}
        arquivos = glob.glob(os.path.join(str(UPLOADS_RAW), f"*{tipo}*.csv"))
        if not arquivos:
            return {"erro": f"Arquivo do tipo {tipo} nao encontrado."}
        arquivo = max(arquivos, key=os.path.getctime)

    dados = []
    try:
        with open(arquivo, "r", encoding="latin-1", errors="ignore") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if row and any(row):
                    dados.append([col.strip().replace(chr(34), "") for col in row])
    except Exception as e:
        return {"erro": str(e)}

    return {"tipo": tipo, "arquivo": os.path.basename(arquivo), "dados": dados}


@router.delete("/api/excluir_relatorio/{nome_arquivo}")
def excluir_relatorio_csv(nome_arquivo: str, request: Request):
    if ".." in nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
        raise HTTPException(status_code=400, detail="Nome de arquivo invalido.")

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            ent_id = resolver_entidade_id(request, conn=conn)
            if ent_id is not None:
                cur.execute(
                    "DELETE FROM arquivos_importados WHERE nome_arquivo = %s AND entidade_id = %s",
                    (nome_arquivo, ent_id),
                )
            else:
                cur.execute("DELETE FROM arquivos_importados WHERE nome_arquivo = %s", (nome_arquivo,))
        conn.commit()
    finally:
        conn.close()

    caminho = Path(UPLOADS_RAW) / nome_arquivo
    if caminho.exists():
        try:
            os.remove(caminho)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Erro ao excluir: " + str(e))

    return {"ok": True, "mensagem": "Arquivo excluido: " + nome_arquivo}


@router.get("/{nome_pagina}", response_class=HTMLResponse)
def rota_pagina_html(nome_pagina: str):
    if ".." in nome_pagina or "/" in nome_pagina or "\\" in nome_pagina:
        raise HTTPException(status_code=400, detail="Nome de pagina invalido")
    stem = nome_pagina[:-5] if nome_pagina.endswith(".html") else nome_pagina
    if not stem:
        raise HTTPException(status_code=404, detail="Pagina nao encontrada")
    arq = (_FRONTEND_DIR / f"{stem}.html").resolve()
    base = _FRONTEND_DIR.resolve()
    if base not in arq.parents or not arq.exists() or not arq.is_file():
        raise HTTPException(status_code=404, detail=f"{stem}.html nao encontrado")
    return FileResponse(str(arq), media_type="text/html; charset=utf-8")
