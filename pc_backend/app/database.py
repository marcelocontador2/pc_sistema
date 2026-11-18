import psycopg2
from psycopg2.extras import RealDictCursor
from .config import PG_CONFIG


def get_db():
    """
    Retorna uma conexão com o PostgreSQL.
    Uso: 
        conn = get_db()
        cur = conn.cursor()
        ...
        conn.close()
    """
    return psycopg2.connect(**PG_CONFIG)


def get_db_dict():
    """
    Retorna uma conexão com o PostgreSQL com cursor que retorna dicionários.
    Uso:
        conn = get_db_dict()
        cur = conn.cursor()
        cur.execute("SELECT ...")
        rows = cur.fetchall()  # lista de dicts
        ...
        conn.close()
    """
    return psycopg2.connect(**PG_CONFIG)
