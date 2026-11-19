from datetime import datetime
from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG, PC_FRONTEND, PC_STORAGE

router = APIRouter(tags=["Configuracoes"])


def _get_conn():
    return psycopg2.connect(**PG_CONFIG)


def _garantir_tabelas(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL DEFAULT '',
            data_atualizacao TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes_entidade (
            id SERIAL PRIMARY KEY,
            razao_social TEXT DEFAULT '',
            nome_fantasia TEXT DEFAULT '',
            cnpj TEXT DEFAULT '',
            endereco TEXT DEFAULT '',
            cep TEXT DEFAULT '',
            logradouro TEXT DEFAULT '',
            numero TEXT DEFAULT '',
            complemento TEXT DEFAULT '',
            bairro TEXT DEFAULT '',
            cidade TEXT DEFAULT '',
            uf TEXT DEFAULT '',
            email TEXT DEFAULT '',
            telefone TEXT DEFAULT '',
            contador_nome TEXT DEFAULT '',
            contador_crc TEXT DEFAULT '',
            contador_uf TEXT DEFAULT '',
            contador_cpf TEXT DEFAULT '',
            contador_email TEXT DEFAULT '',
            data_atualizacao TEXT DEFAULT '',
            logo_path TEXT DEFAULT ''
        )
    """)
    cur.execute("ALTER TABLE configuracoes_entidade ADD COLUMN IF NOT EXISTS logo_path TEXT DEFAULT ''")


def _servir_html(nome_arquivo: str):
    arq = Path(PC_FRONTEND) / nome_arquivo
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})
    raise HTTPException(status_code=404, detail=f"{nome_arquivo} nao encontrado")


@router.get("/configuracoes", response_class=HTMLResponse)
@router.get("/configuracoes.html", response_class=HTMLResponse)
def rota_configuracoes():
    return _servir_html("configuracoes.html")


@router.get("/configuracoes_custo_pessoal", response_class=HTMLResponse)
@router.get("/configuracoes_custo_pessoal.html", response_class=HTMLResponse)
def rota_configuracoes_custo_pessoal():
    return _servir_html("configuracoes_custo_pessoal.html")


@router.get("/entidades", response_class=HTMLResponse)
@router.get("/entidades.html", response_class=HTMLResponse)
def rota_entidades():
    return _servir_html("entidades.html")


@router.get("/api/configuracoes")
def get_configuracoes():
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute("SELECT chave, valor FROM configuracoes")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {k: v for k, v in rows}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})


@router.post("/api/configuracoes")
async def post_configuracoes(request: Request):
    try:
        config = await request.json()
        if not isinstance(config, dict):
            return JSONResponse(status_code=400, content={"ok": False, "mensagem": "Payload invalido"})
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        for chave, valor in config.items():
            cur.execute(
                """
                INSERT INTO configuracoes (chave, valor, data_atualizacao)
                VALUES (%s, %s, %s)
                ON CONFLICT (chave) DO UPDATE
                SET valor = EXCLUDED.valor, data_atualizacao = EXCLUDED.data_atualizacao
                """,
                (str(chave), "" if valor is None else str(valor), agora),
            )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "ok": True, "configuracoes": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "erro": str(e)})


@router.get("/api/configuracoes/custo_pessoal")
def api_configuracoes_custo_pessoal_get():
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        row = cur.fetchone()
        cur.close()
        conn.close()
        entidade = row[0] if row and row[0] else "COFEN"
        return {"tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})


@router.post("/api/configuracoes/custo_pessoal")
async def api_configuracoes_custo_pessoal_post(request: Request):
    try:
        dados = await request.json()
        entidade = str(dados.get("tipo_entidade", "COFEN")).upper()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        cur.execute(
            """
            INSERT INTO configuracoes (chave, valor, data_atualizacao)
            VALUES ('tipo_entidade', %s, %s)
            ON CONFLICT (chave) DO UPDATE
            SET valor = EXCLUDED.valor, data_atualizacao = EXCLUDED.data_atualizacao
            """,
            (entidade, agora),
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "ok": True, "tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "erro": str(e)})


_CAMPOS_ENTIDADE = [
    "razao_social",
    "nome_fantasia",
    "cnpj",
    "endereco",
    "cep",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "uf",
    "email",
    "telefone",
    "contador_nome",
    "contador_crc",
    "contador_uf",
    "contador_cpf",
    "contador_email",
]


@router.get("/api/configuracoes/entidade")
def obter_entidade(id: int = None):
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        _garantir_tabelas(cur)
        conn.commit()
        if id is not None:
            cur.execute("SELECT * FROM configuracoes_entidade WHERE id = %s", (id,))
        else:
            cur.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            base = {campo: "" for campo in _CAMPOS_ENTIDADE}
            base["id"] = None
            base["logo_path"] = ""
            return base
        return dict(row)
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})


@router.post("/api/configuracoes/entidade")
async def salvar_entidade(request: Request):
    try:
        body = await request.json()
        if not isinstance(body, dict):
            return {"ok": False, "mensagem": "Dados invalidos."}
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valores = ["" if body.get(c) is None else str(body.get(c)) for c in _CAMPOS_ENTIDADE]
        entidade_id = body.get("id")

        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)

        if entidade_id:
            set_sql = ", ".join(f"{c} = %s" for c in _CAMPOS_ENTIDADE) + ", data_atualizacao = %s"
            cur.execute(
                f"UPDATE configuracoes_entidade SET {set_sql} WHERE id = %s",
                valores + [agora, int(entidade_id)],
            )
            novo_id = int(entidade_id)
        else:
            cols_sql = ", ".join(_CAMPOS_ENTIDADE) + ", data_atualizacao"
            placeholders = ", ".join(["%s"] * (len(_CAMPOS_ENTIDADE) + 1))
            cur.execute(
                f"INSERT INTO configuracoes_entidade ({cols_sql}) VALUES ({placeholders}) RETURNING id",
                valores + [agora],
            )
            novo_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True, "id": novo_id, "mensagem": "Configuracoes salvas com sucesso!"}
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro no banco: {e}"}


@router.post("/api/configuracoes/logo")
async def upload_logo(file: UploadFile = File(...), entidade_id: str = Form(None)):
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in {"png", "jpg", "jpeg"}:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PNG ou JPG.")

    pasta_logos = Path(PC_STORAGE) / "uploads_logos"
    pasta_logos.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho_completo = pasta_logos / nome_arquivo

    with caminho_completo.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    conn = _get_conn()
    cur = conn.cursor()
    _garantir_tabelas(cur)
    if entidade_id:
        cur.execute("UPDATE configuracoes_entidade SET logo_path = %s WHERE id = %s", (nome_arquivo, int(entidade_id)))
    else:
        cur.execute("SELECT id FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE configuracoes_entidade SET logo_path = %s WHERE id = %s", (nome_arquivo, row[0]))
        else:
            cur.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', %s)", (nome_arquivo,))
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}


@router.get("/api/configuracoes/migrar_logo")
def migrar_logo():
    conn = _get_conn()
    cur = conn.cursor()
    _garantir_tabelas(cur)
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "mensagem": "Coluna logo_path verificada/adicionada em configuracoes_entidade."}


@router.get("/static_logos/{nome_arq}")
def servir_logo_estatico(nome_arq: str):
    nome_limpo = Path(nome_arq).name
    candidatos = [
        Path(PC_STORAGE) / "uploads_logos" / nome_limpo,
        Path(PC_FRONTEND) / nome_limpo,
    ]
    for arq in candidatos:
        if arq.exists() and arq.is_file():
            ext = arq.suffix.lower()
            media = "image/png" if ext == ".png" else ("image/jpeg" if ext in (".jpg", ".jpeg") else "application/octet-stream")
            return FileResponse(str(arq.resolve()), media_type=media, headers={"Cache-Control": "no-cache"})
    raise HTTPException(status_code=404, detail="Logo nao encontrada")
