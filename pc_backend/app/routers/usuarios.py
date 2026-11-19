import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG, PC_FRONTEND

router = APIRouter(tags=["Usuarios"])

_SALT_SENHA = "sigos_salt_2026_"


def _get_conn():
    return psycopg2.connect(**PG_CONFIG)


def _garantir_tabelas(cur):
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            perfil TEXT NOT NULL DEFAULT 'user',
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            entidade_id INTEGER REFERENCES configuracoes_entidade(id) ON DELETE SET NULL
        )
    """)


def _hash_senha(senha: str) -> str:
    return hashlib.sha256((_SALT_SENHA + senha).encode("utf-8")).hexdigest()


def _servir_html(nome_arquivo: str):
    arq = Path(PC_FRONTEND) / nome_arquivo
    if arq.exists() and arq.is_file():
        return FileResponse(str(arq.resolve()), media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})
    raise HTTPException(status_code=404, detail=f"{nome_arquivo} nao encontrado")


@router.get("/usuarios", response_class=HTMLResponse)
@router.get("/usuarios.html", response_class=HTMLResponse)
def rota_usuarios():
    return _servir_html("usuarios.html")


@router.get("/login", response_class=HTMLResponse)
@router.get("/login.html", response_class=HTMLResponse)
def rota_login():
    return _servir_html("login.html")


@router.get("/api/entidades")
def listar_entidades():
    try:
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute("SELECT id, razao_social, nome_fantasia, cnpj FROM configuracoes_entidade ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})


@router.delete("/api/entidades/{id}")
def deletar_entidade(id: int):
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        cur.execute("DELETE FROM configuracoes_entidade WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True, "mensagem": "Entidade excluida com sucesso"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "mensagem": f"Erro ao excluir entidade: {e}"})


@router.get("/api/usuarios")
def listar_usuarios():
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute("""
            SELECT u.id, u.nome, u.email, u.perfil, u.ativo, u.entidade_id, e.nome_fantasia
            FROM usuarios u
            LEFT JOIN configuracoes_entidade e ON u.entidade_id = e.id
            ORDER BY u.id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        usuarios = [
            {
                "id": r[0],
                "nome": r[1],
                "email": r[2],
                "perfil": r[3],
                "ativo": r[4],
                "entidade_id": r[5],
                "entidade_nome": r[6] or "Sem entidade",
            }
            for r in rows
        ]
        return {"ok": True, "usuarios": usuarios}
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao listar usuarios: {e}"}


@router.post("/api/usuarios")
def salvar_usuario(body: dict):
    nome = str(body.get("nome") or "").strip()
    email = str(body.get("email") or "").strip()
    senha = str(body.get("senha") or "")
    perfil = str(body.get("perfil") or "user").strip()
    entidade_id = body.get("entidade_id")
    entidade_id = int(entidade_id) if entidade_id not in (None, "", "null") else None
    usuario_id = body.get("id")

    if not nome or not email:
        return {"ok": False, "mensagem": "Nome e e-mail sao obrigatorios."}

    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)

        if usuario_id:
            if senha:
                senha_hash = _hash_senha(senha)
                cur.execute(
                    """
                    UPDATE usuarios
                    SET nome = %s, email = %s, senha_hash = %s, perfil = %s, entidade_id = %s
                    WHERE id = %s
                    """,
                    (nome, email, senha_hash, perfil, entidade_id, int(usuario_id)),
                )
            else:
                cur.execute(
                    """
                    UPDATE usuarios
                    SET nome = %s, email = %s, perfil = %s, entidade_id = %s
                    WHERE id = %s
                    """,
                    (nome, email, perfil, entidade_id, int(usuario_id)),
                )
        else:
            if not senha:
                return {"ok": False, "mensagem": "Senha e obrigatoria para novos usuarios."}
            senha_hash = _hash_senha(senha)
            cur.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, perfil, entidade_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome, email, senha_hash, perfil, entidade_id),
            )

        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True, "mensagem": "Usuario salvo com sucesso!"}
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao salvar usuario: {e}"}


@router.post("/api/login")
def login(body: dict):
    email = str(body.get("email") or "").strip()
    senha = str(body.get("senha") or "")
    if not email or not senha:
        return {"ok": False, "mensagem": "E-mail e senha sao obrigatorios."}

    senha_hash = _hash_senha(senha)
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute(
            """
            SELECT id, nome, email, perfil, entidade_id
            FROM usuarios
            WHERE email = %s AND senha_hash = %s AND ativo = TRUE
            """,
            (email, senha_hash),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {"ok": False, "mensagem": "Credenciais invalidas."}
        return {
            "ok": True,
            "usuario": {
                "id": row[0],
                "nome": row[1],
                "email": row[2],
                "perfil": row[3],
                "entidade_id": row[4],
            },
        }
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao autenticar: {e}"}
