import json
import re
import unicodedata
import psycopg2
from pc_backend.app.config import PG_CONFIG

def _slug_conta(texto: str) -> str:
    if not texto:
        return "item"
    s = unicodedata.normalize("NFKD", str(texto))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.lower()).strip("_")
    return s[:180] or "item"

def garantir_tabela_memoria(cur) -> None:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contas_demonstrativos_memoria (
            id BIGSERIAL PRIMARY KEY,
            modulo VARCHAR(80) NOT NULL,
            periodo VARCHAR(80) NOT NULL,
            conta_chave VARCHAR(200) NOT NULL,
            descricao TEXT NOT NULL,
            valor NUMERIC(18, 2) NOT NULL DEFAULT 0,
            dados_json JSONB,
            atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_contas_demo_mem UNIQUE (modulo, periodo, conta_chave)
        )
    """)

def salvar_contas_memoria(modulo: str, periodo: str, itens: list[dict]) -> int:
    """
    Persiste cada conta/item extraido no PostgreSQL para o periodo informado.
    Se a conta nao existir para (modulo, periodo, conta_chave), cria com novo id.
    Se ja existir, atualiza valor e dados_json mantendo o id.
    Cada item em `itens` pode conter: chave (opcional), descricao, valor, extra (dict opcional).
    """
    if not itens:
        return 0
    conn = psycopg2.connect(**PG_CONFIG)
    afetados = 0
    try:
        cur = conn.cursor()
        garantir_tabela_memoria(cur)
        sql = """
            INSERT INTO contas_demonstrativos_memoria
                (modulo, periodo, conta_chave, descricao, valor, dados_json, atualizado_em)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
            ON CONFLICT (modulo, periodo, conta_chave)
            DO UPDATE SET
                descricao = EXCLUDED.descricao,
                valor = EXCLUDED.valor,
                dados_json = EXCLUDED.dados_json,
                atualizado_em = NOW()
        """
        for idx, item in enumerate(itens):
            desc = str(item.get("descricao") or item.get("chave") or f"item_{idx+1}").strip()
            chave = str(item.get("chave") or "").strip() or f"{_slug_conta(desc)}_{idx+1}"
            chave = chave[:200]
            try:
                val = float(item.get("valor") or 0.0)
            except (TypeError, ValueError):
                val = 0.0
            payload = item.get("extra") if isinstance(item.get("extra"), dict) else item
            cur.execute(sql, (modulo, periodo, chave, desc, val, json.dumps(payload, ensure_ascii=False, default=str)))
            afetados += 1
        conn.commit()
        cur.close()
    finally:
        conn.close()
    return afetados

def carregar_contas_memoria(modulo: str, periodo: str) -> list[dict]:
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor()
        garantir_tabela_memoria(cur)
        cur.execute("""
            SELECT id, conta_chave, descricao, valor, dados_json, atualizado_em
            FROM contas_demonstrativos_memoria
            WHERE modulo = %s AND periodo = %s
            ORDER BY id ASC
        """, (modulo, periodo))
        rows = cur.fetchall()
        cur.close()
    finally:
        conn.close()
    saida = []
    for r in rows:
        extra = r[4]
        if isinstance(extra, str):
            try:
                extra = json.loads(extra)
            except Exception:
                extra = {}
        saida.append({
            "id": r[0],
            "chave": r[1],
            "descricao": r[2],
            "valor": float(r[3] or 0.0),
            "dados_json": extra or {},
            "atualizado_em": r[5].isoformat() if r[5] else None,
        })
    return saida
