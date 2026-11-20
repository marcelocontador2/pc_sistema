import hashlib
import os
import secrets
import smtplib
from email.message import EmailMessage
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG, PC_FRONTEND

router = APIRouter(tags=["Usuarios"])

_SALT_SENHA = "sigos_salt_2026_"
_REMETENTE_PADRAO = "spccofen@gmail.com"


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
            usuario TEXT,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            perfil TEXT NOT NULL DEFAULT 'user',
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            entidade_id INTEGER REFERENCES configuracoes_entidade(id) ON DELETE SET NULL
        )
    """)
    cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS usuario TEXT")
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_usuario_unique
        ON usuarios (LOWER(TRIM(usuario)))
        WHERE usuario IS NOT NULL AND TRIM(usuario) <> ''
    """)


def _hash_senha(senha: str) -> str:
    return hashlib.sha256((_SALT_SENHA + senha).encode("utf-8")).hexdigest()


def _normalizar_usuario(u: str) -> str:
    return "".join(ch for ch in u.strip().lower() if ch.isalnum() or ch in ("_", ".", "-"))


def _enviar_email_recuperacao(destinatario: str, usuario_login: str, nome: str, nova_senha: str):
    remetente = (os.getenv("SMTP_REMETENTE") or _REMETENTE_PADRAO).strip()
    senha_app = (os.getenv("SMTP_SENHA_APP") or os.getenv("GMAIL_APP_PASSWORD") or "").strip()
    smtp_host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT") or "587")

    if not senha_app:
        raise RuntimeError(
            f"Senha de aplicativo SMTP nao configurada para {remetente}. "
            "Defina a variavel de ambiente SMTP_SENHA_APP."
        )

    msg = EmailMessage()
    msg["Subject"] = "Recuperacao de Senha - Login SPC"
    msg["From"] = remetente
    msg["To"] = destinatario
    msg.set_content(
        f"Ola, {nome}!\n\n"
        f"Foi solicitada a redefinicao de senha para o acesso ao SPC (Sistema de Prestacao de Contas).\n\n"
        f"Usuario: {usuario_login}\n"
        f"Nova senha temporaria: {nova_senha}\n\n"
        f"Recomendamos alterar essa senha apos o login.\n"
        f"Caso voce nao tenha solicitado, entre em contato com o administrador.\n"
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remetente, senha_app)
        server.send_message(msg)


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
            SELECT u.id, u.nome, u.usuario, u.email, u.perfil, u.ativo, u.entidade_id, e.nome_fantasia
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
                "usuario": r[2] or "",
                "email": r[3],
                "perfil": r[4],
                "ativo": r[5],
                "entidade_id": r[6],
                "entidade_nome": r[7] or "Sem entidade",
            }
            for r in rows
        ]
        return {"ok": True, "usuarios": usuarios}
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao listar usuarios: {e}"}


@router.post("/api/usuarios")
def salvar_usuario(body: dict):
    nome = str(body.get("nome") or "").strip()
    usuario = _normalizar_usuario(str(body.get("usuario") or ""))
    email = str(body.get("email") or "").strip()
    senha = str(body.get("senha") or "")
    perfil = str(body.get("perfil") or "user").strip()
    entidade_id = body.get("entidade_id")
    entidade_id = int(entidade_id) if entidade_id not in (None, "", "null") else None
    usuario_id = body.get("id")

    if not nome or not usuario or not email:
        return {"ok": False, "mensagem": "Nome, usuario e e-mail sao obrigatorios."}

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
                    SET nome = %s, usuario = %s, email = %s, senha_hash = %s, perfil = %s, entidade_id = %s
                    WHERE id = %s
                    """,
                    (nome, usuario, email, senha_hash, perfil, entidade_id, int(usuario_id)),
                )
            else:
                cur.execute(
                    """
                    UPDATE usuarios
                    SET nome = %s, usuario = %s, email = %s, perfil = %s, entidade_id = %s
                    WHERE id = %s
                    """,
                    (nome, usuario, email, perfil, entidade_id, int(usuario_id)),
                )
        else:
            if not senha:
                return {"ok": False, "mensagem": "Senha e obrigatoria para novos usuarios."}
            senha_hash = _hash_senha(senha)
            cur.execute(
                """
                INSERT INTO usuarios (nome, usuario, email, senha_hash, perfil, entidade_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome, usuario, email, senha_hash, perfil, entidade_id),
            )

        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True, "mensagem": "Usuario salvo com sucesso!"}
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao salvar usuario: {e}"}


@router.post("/api/login")
def login(body: dict):
    usuario = _normalizar_usuario(str(body.get("usuario") or body.get("login") or ""))
    senha = str(body.get("senha") or "")
    if not usuario or not senha:
        return {"ok": False, "mensagem": "Usuario e senha sao obrigatorios."}

    senha_hash = _hash_senha(senha)
    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute(
            """
            SELECT id, nome, usuario, email, perfil, entidade_id
            FROM usuarios
            WHERE LOWER(TRIM(usuario)) = %s AND senha_hash = %s AND ativo = TRUE
            """,
            (usuario, senha_hash),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {"ok": False, "mensagem": "Usuario ou senha invalidos."}
        return {
            "ok": True,
            "usuario": {
                "id": row[0],
                "nome": row[1],
                "usuario": row[2],
                "email": row[3],
                "perfil": row[4],
                "entidade_id": row[5],
            },
        }
    except Exception as e:
        return {"ok": False, "mensagem": f"Erro ao autenticar: {e}"}


@router.post("/api/esqueci-senha")
def esqueci_senha(body: dict):
    identificador = str(body.get("identificador") or body.get("usuario") or body.get("email") or "").strip()
    if not identificador:
        return {"ok": False, "mensagem": "Informe o usuario ou e-mail cadastrado."}

    try:
        conn = _get_conn()
        cur = conn.cursor()
        _garantir_tabelas(cur)
        conn.commit()
        cur.execute(
            """
            SELECT id, nome, usuario, email
            FROM usuarios
            WHERE ativo = TRUE
              AND (LOWER(TRIM(usuario)) = LOWER(%s) OR LOWER(TRIM(email)) = LOWER(%s))
            """,
            (identificador, identificador),
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return {"ok": False, "mensagem": "Usuario ou e-mail nao encontrado."}

        uid, nome, usuario_login, email_destino = row
        if not email_destino:
            cur.close()
            conn.close()
            return {"ok": False, "mensagem": "Usuario sem e-mail cadastrado para envio."}

        nova_senha = secrets.token_urlsafe(8)
        nova_hash = _hash_senha(nova_senha)
        _enviar_email_recuperacao(email_destino, usuario_login or email_destino, nome, nova_senha)

        cur.execute("UPDATE usuarios SET senha_hash = %s WHERE id = %s", (nova_hash, uid))
        conn.commit()
        cur.close()
        conn.close()
        return {
            "ok": True,
            "mensagem": f"Nova senha enviada por e-mail ({_REMETENTE_PADRAO}) para {email_destino}.",
        }
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}
