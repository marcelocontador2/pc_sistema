"""Drop-in replacement for sqlite3 module that uses PostgreSQL."""
import re
import sys
import psycopg2

try:
    from app.core.database import DB_CONFIG as PG_CONFIG
except ImportError:
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database",
        "user": "postgres", "password": "pc_admin_2026",
    }

Error = psycopg2.Error
DatabaseError = psycopg2.DatabaseError
OperationalError = psycopg2.OperationalError
IntegrityError = psycopg2.IntegrityError
ProgrammingError = psycopg2.ProgrammingError
NotSupportedError = psycopg2.NotSupportedError
DataError = psycopg2.DataError
InterfaceError = psycopg2.InterfaceError
InternalError = psycopg2.InternalError


class Row:
    __slots__ = ("_data", "_idx")
    def __init__(self, data, columns):
        self._data = tuple(data)
        self._idx = {c: i for i, c in enumerate(columns)}
    def __getitem__(self, key):
        if isinstance(key, str):
            return self._data[self._idx[key]]
        return self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
    def __repr__(self): return f"Row({dict(zip(self._idx.keys(), self._data))})"
    def keys(self): return list(self._idx.keys())
    def get(self, key, default=None):
        try: return self[key]
        except (KeyError, IndexError): return default


def _translate_sql(sql):
    if sql is None:
        return sql
    s = sql
    upper = s.strip().upper()
    if upper.startswith("PRAGMA"):
        return None
    if "SQLITE_MASTER" in upper:
        s = re.sub(
            r"\bsqlite_master\b",
            "(SELECT tablename AS name, 'table' AS type, NULL AS sql "
            "FROM pg_tables WHERE schemaname='public') AS _sqm",
            s, flags=re.IGNORECASE,
        )
    s = re.sub(r"\bAUTOINCREMENT\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bINTEGER\s+PRIMARY\s+KEY\b", "BIGSERIAL PRIMARY KEY", s, flags=re.IGNORECASE)
    if re.search(r"INSERT\s+OR\s+IGNORE", s, re.IGNORECASE):
        s = re.sub(r"INSERT\s+OR\s+IGNORE", "INSERT", s, flags=re.IGNORECASE)
        s = s.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    s = re.sub(r"INSERT\s+OR\s+REPLACE", "INSERT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bIFNULL\s*\(", "COALESCE(", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdatetime\s*\(\s*'now'\s*\)", "CURRENT_TIMESTAMP", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdate\s*\(\s*'now'\s*\)", "CURRENT_DATE", s, flags=re.IGNORECASE)
    s = s.replace("?", "%s")
    return s


class _CompatCursor:
    def __init__(self, pg_conn):
        self._pg = pg_conn
        self._cur = pg_conn.cursor()
        self.row_factory = None
        self._columns = []
        self._lastrowid = None
    @property
    def lastrowid(self): return self._lastrowid
    @property
    def description(self):
        if self._cur.description:
            return [(d.name, None, None, None, None, None, None) for d in self._cur.description]
        return None
    def execute(self, sql, params=None):
        translated = _translate_sql(sql)
        if translated is None:
            self._columns = []; self._lastrowid = None
            return self
        try:
            if params is not None and len(params) > 0:
                self._cur.execute(translated, params)
            else:
                self._cur.execute(translated)
        except Exception:
            try: self._pg.rollback()
            except Exception: pass
            raise
        self._columns = [d.name for d in self._cur.description] if self._cur.description else []
        upper = sql.strip().upper()
        if upper.startswith("INSERT") or upper.startswith("REPLACE"):
            try:
                self._cur.execute("SAVEPOINT _lv_check")
                self._cur.execute("SELECT lastval()")
                r = self._cur.fetchone()
                self._lastrowid = r[0] if r else None
                self._cur.execute("RELEASE SAVEPOINT _lv_check")
            except Exception:
                try:
                    self._cur.execute("ROLLBACK TO SAVEPOINT _lv_check")
                except Exception:
                    pass
                self._lastrowid = None
        return self
    def executemany(self, sql, seq_params):
        translated = _translate_sql(sql)
        if translated is None: return self
        try:
            self._cur.executemany(translated, seq_params)
        except Exception:
            try: self._pg.rollback()
            except Exception: pass
            raise
        return self
    def fetchone(self):
        r = self._cur.fetchone()
        if r is None: return None
        return Row(r, self._columns) if self.row_factory is Row else r
    def fetchall(self):
        rows = self._cur.fetchall()
        return [Row(r, self._columns) for r in rows] if self.row_factory is Row else rows
    def fetchmany(self, size=None):
        rows = self._cur.fetchmany(size or self._cur.arraysize)
        return [Row(r, self._columns) for r in rows] if self.row_factory is Row else rows
    def close(self):
        try: self._cur.close()
        except Exception: pass
    def __iter__(self): return iter(self.fetchall())


class _CompatConnection:
    def __init__(self, *args, **kwargs):
        self._pg = psycopg2.connect(**PG_CONFIG)
        self._pg.autocommit = False
        self.row_factory = None
    def cursor(self):
        cur = _CompatCursor(self._pg)
        cur.row_factory = self.row_factory
        return cur
    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)
    def executemany(self, sql, seq):
        return self.cursor().executemany(sql, seq)
    def commit(self): self._pg.commit()
    def rollback(self): self._pg.rollback()
    def close(self):
        try: self._pg.close()
        except Exception: pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type: self.rollback()
        else: self.commit()
        self.close()


def connect(path=None, timeout=None, **kwargs):
    return _CompatConnection()


Connection = _CompatConnection


def patch():
    import types
    mod = types.ModuleType("sqlite3")
    mod.connect = connect
    mod.Connection = Connection
    mod.Cursor = _CompatCursor
    mod.Row = Row
    mod.Error = Error
    mod.DatabaseError = DatabaseError
    mod.OperationalError = OperationalError
    mod.IntegrityError = IntegrityError
    mod.ProgrammingError = ProgrammingError
    mod.NotSupportedError = NotSupportedError
    mod.DataError = DataError
    mod.InterfaceError = InterfaceError
    mod.InternalError = InternalError
    mod.PARSE_DECLTYPES = 1
    mod.PARSE_COLNAMES = 2
    mod.complete_statement = lambda s: s.strip().endswith(";")
    mod.sqlite_version = "3.0.0-pg"
    mod.sqlite_version_info = (3, 0, 0)
    mod.version = "2.0.0-pg"
    mod.version_info = (2, 0, 0)
    sys.modules["sqlite3"] = mod
    return mod


# Auto-patch ao importar
patch()
