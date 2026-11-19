"""
Gerenciamento dinamico de conclusoes, observacoes e comentarios no PostgreSQL,
isolado por item_numero / item, periodo e ano.
"""
import json
import re
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from pc_backend.app.config import PG_CONFIG

ITENS_PADRAO: list[dict[str, Any]] = [
    {"item_numero": 1, "item": "1. conferencia", "slug": "conferencia", "titulo": "Conferencia"},
    {"item_numero": 2, "item": "2. integridade", "slug": "integridade", "titulo": "Integridade"},
    {"item_numero": 3, "item": "3. panorama", "slug": "panorama", "titulo": "Panorama"},
    {"item_numero": 4, "item": "4. receitas", "slug": "receitas", "titulo": "Receitas"},
    {"item_numero": 5, "item": "5. despesas", "slug": "despesas", "titulo": "Despesas"},
    {"item_numero": 6, "item": "6. analise_orcamentaria", "slug": "analise_orcamentaria", "titulo": "Analise Orcamentaria"},
    {"item_numero": 7, "item": "7. balanco_financeiro", "slug": "balanco_financeiro", "titulo": "Balanco Financeiro"},
    {"item_numero": 8, "item": "8. analise_financeira", "slug": "analise_financeira", "titulo": "Analise Financeira"},
    {"item_numero": 9, "item": "9. bp", "slug": "bp", "titulo": "Balanco Patrimonial"},
    {"item_numero": 10, "item": "10. dvp", "slug": "dvp", "titulo": "Demonstracao das Variacoes Patrimoniais"},
    {"item_numero": 11, "item": "11. dfc", "slug": "dfc", "titulo": "Demonstracao dos Fluxos de Caixa"},
    {"item_numero": 12, "item": "12. dmpl", "slug": "dmpl", "titulo": "Demonstracao das Mutacoes do Patrimonio Liquido"},
    {"item_numero": 13, "item": "13. liquidez", "slug": "liquidez", "titulo": "Liquidez"},
    {"item_numero": 14, "item": "14. relatorio_consolidado", "slug": "relatorio_consolidado", "titulo": "Relatorio Consolidado"},
]


def normalizar_item(item: str, item_numero: int | None = None) -> tuple[int, str]:
    texto = (item or "").strip()
    numero = item_numero
    if numero is None:
        match = re.match(r"^(\d+)\s*[\.\-\):]?\s*(.*)$", texto)
        if match:
            numero = int(match.group(1))
            resto = match.group(2).strip()
            if resto and not texto.startswith(f"{numero}."):
                texto = f"{numero}. {resto}"
            elif not resto:
                texto = f"{numero}. item"
        else:
            numero = 0
            texto = texto or "0. geral"
    else:
        match = re.match(r"^(\d+)\s*[\.\-\):]?\s*(.*)$", texto)
        if match and match.group(2).strip():
            texto = f"{numero}. {match.group(2).strip()}"
        elif not texto:
            texto = f"{numero}. item"
        elif not texto.startswith(f"{numero}."):
            texto = f"{numero}. {texto}"
    return int(numero), texto


def garantir_tabela_notas(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS registro_conclusao_observacoes (
                id SERIAL PRIMARY KEY,
                item_numero INTEGER NOT NULL DEFAULT 0,
                item VARCHAR(100) NOT NULL DEFAULT '0. geral',
                periodo VARCHAR(50) NOT NULL,
                ano INTEGER NOT NULL,
                tipo VARCHAR(30) NOT NULL DEFAULT 'observacao',
                texto TEXT NOT NULL,
                metadados JSONB,
                registrado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            ALTER TABLE registro_conclusao_observacoes
            ADD COLUMN IF NOT EXISTS item_numero INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS item VARCHAR(100) NOT NULL DEFAULT '0. geral',
            ADD COLUMN IF NOT EXISTS tipo VARCHAR(30) NOT NULL DEFAULT 'observacao',
            ADD COLUMN IF NOT EXISTS texto TEXT,
            ADD COLUMN IF NOT EXISTS metadados JSONB,
            ADD COLUMN IF NOT EXISTS registrado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_registro_conclusao_obs_item_num_ano_per
            ON registro_conclusao_observacoes (item_numero, item, ano DESC, periodo, registrado_em DESC)
            """
        )


def salvar_nota_item(
    item: str,
    periodo: str,
    ano: int,
    texto: str,
    tipo: str = "observacao",
    item_numero: int | None = None,
    metadados: dict[str, Any] | None = None,
) -> dict[str, Any]:
    num, rotulo = normalizar_item(item, item_numero)
    tipo_limpo = (tipo or "observacao").strip().lower()
    if tipo_limpo not in ("conclusao", "observacao", "comentario"):
        tipo_limpo = "observacao"

    meta_final = dict(metadados or {})
    meta_final.setdefault("item_numero", num)
    meta_final.setdefault("item", rotulo)
    meta_final.setdefault("periodo", periodo)
    meta_final.setdefault("ano", int(ano))

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        garantir_tabela_notas(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO registro_conclusao_observacoes
                    (item_numero, item, periodo, ano, tipo, texto, metadados)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id, item_numero, item, periodo, ano, tipo, texto, metadados, registrado_em
                """,
                (
                    num,
                    rotulo,
                    periodo.strip(),
                    int(ano),
                    tipo_limpo,
                    texto.strip(),
                    json.dumps(meta_final, ensure_ascii=False),
                ),
            )
            row = dict(cur.fetchone())
        conn.commit()
        return row
    finally:
        conn.close()


def listar_notas_item(
    item: str | None = None,
    item_numero: int | None = None,
    periodo: str | None = None,
    ano: int | None = None,
    tipo: str | None = None,
) -> list[dict[str, Any]]:
    filtros: list[str] = []
    params: list[Any] = []

    if item_numero is not None:
        filtros.append("item_numero = %s")
        params.append(int(item_numero))
    elif item and item.strip():
        num, rotulo = normalizar_item(item, None)
        if num > 0 and item.strip().isdigit():
            filtros.append("item_numero = %s")
            params.append(num)
        else:
            filtros.append("(LOWER(item) = LOWER(%s) OR LOWER(item) LIKE LOWER(%s))")
            params.append(rotulo)
            params.append(f"%{item.strip()}%")

    if periodo and periodo.strip():
        filtros.append("periodo = %s")
        params.append(periodo.strip())

    if ano is not None:
        filtros.append("ano = %s")
        params.append(int(ano))

    if tipo and tipo.strip():
        filtros.append("LOWER(tipo) = LOWER(%s)")
        params.append(tipo.strip())

    where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        garantir_tabela_notas(conn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id, item_numero, item, periodo, ano, tipo, texto, metadados, registrado_em
                FROM registro_conclusao_observacoes
                {where_sql}
                ORDER BY item_numero ASC, ano DESC, periodo DESC, id ASC
                """,
                params,
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
