import sqlite3
import psycopg2
import os

SQLITE_PATH = "pc_storage/banco_dados.db"
PG_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026",
}

SKIP_TABLES = {"sqlite_sequence"}
PG_KEEP_TABLES = {"balancete_linha", "demonstracao_resumo",
                  "documento_importado", "matriz_calculo", "periodo"}


def sqlite_type_to_pg(t):
    if not t:
        return "TEXT"
    t = t.upper()
    if "INT" in t:
        return "BIGINT"
    if "REAL" in t or "FLOA" in t or "DOUB" in t:
        return "DOUBLE PRECISION"
    if "BLOB" in t:
        return "BYTEA"
    if "BOOL" in t:
        return "BOOLEAN"
    if "NUM" in t or "DEC" in t:
        return "NUMERIC"
    if "DATE" in t or "TIME" in t:
        return "TIMESTAMP"
    return "TEXT"


def get_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table}")')
    return cur.fetchall()


def build_create_sql(table, cols):
    col_defs = []
    pk_cols = []
    has_serial = False
    pk_col_name = None
    single_int_pk = len([c for c in cols if c[5] > 0]) == 1 and any(
        c[5] > 0 and "INT" in (c[2] or "").upper() for c in cols
    )

    for cid, name, ctype, notnull, dflt, pk in cols:
        pg_type = sqlite_type_to_pg(ctype)
        if pk > 0 and single_int_pk:
            pg_type = "BIGSERIAL"
            has_serial = True
            pk_col_name = name
        col_def = f'"{name}" {pg_type}'
        if pk > 0:
            pk_cols.append((pk, name))
        if notnull and pk == 0:
            col_def += " NOT NULL"
        if dflt is not None:
            col_def += f" DEFAULT {dflt}"
        col_defs.append(col_def)

    if len(pk_cols) > 1:
        pk_cols.sort()
        names = ", ".join(f'"{n}"' for _, n in pk_cols)
        col_defs.append(f"PRIMARY KEY ({names})")
    elif len(pk_cols) == 1 and not has_serial:
        col_defs.append(f'PRIMARY KEY ("{pk_cols[0][1]}")')

    return f'CREATE TABLE "{table}" ({", ".join(col_defs)})', has_serial, pk_col_name


def main():
    if not os.path.exists(SQLITE_PATH):
        print(f"ERRO: {SQLITE_PATH} nao encontrado")
        return

    print("Conectando...")
    conn_s = sqlite3.connect(SQLITE_PATH)
    conn_p = psycopg2.connect(**PG_CONFIG)

    cur_s = conn_s.cursor()
    cur_s.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur_s.fetchall() if r[0] not in SKIP_TABLES]

    print(f"Migrando {len(tables)} tabelas SQLite -> PostgreSQL")
    print("=" * 60)

    for table in tables:
        if table in PG_KEEP_TABLES:
            print(f"[{table}] JA EXISTE no PG com dados - PULANDO")
            continue

        cols = get_columns(conn_s, table)
        if not cols:
            print(f"[{table}] sem colunas - PULANDO")
            continue

        create_sql, has_serial, pk_col = build_create_sql(table, cols)

        try:
            cur_p = conn_p.cursor()
            cur_p.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            cur_p.execute(create_sql)

            col_names = [c[1] for c in cols]
            col_list = ", ".join(f'"{n}"' for n in col_names)
            ph = ", ".join(["%s"] * len(col_names))
            insert_sql = f'INSERT INTO "{table}" ({col_list}) VALUES ({ph})'

            cur_s.execute(f'SELECT * FROM "{table}"')
            rows = cur_s.fetchall()

            n = 0
            for row in rows:
                try:
                    cur_p.execute(insert_sql, row)
                    n += 1
                except Exception as e:
                    print(f"  [{table}] ERRO linha: {e}")
                    conn_p.rollback()

            if has_serial and pk_col and n > 0:
                cur_p.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{pk_col}'), "
                    f'COALESCE((SELECT MAX("{pk_col}") FROM "{table}"), 0) + 1, false)'
                )

            conn_p.commit()
            print(f"[{table}] OK - {n}/{len(rows)} linhas")
        except Exception as e:
            print(f"[{table}] FALHOU: {e}")
            conn_p.rollback()

    conn_s.close()
    conn_p.close()
    print("=" * 60)
    print("MIGRACAO CONCLUIDA")


if __name__ == "__main__":
    main()
