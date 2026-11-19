import sys
import psycopg2
from pc_backend.app.config import PG_CONFIG

sys.stdout.reconfigure(encoding="utf-8")

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()

# Pega todos os IDs
cur.execute("SELECT id, periodo FROM historico_relatorio_consolidado")
rows = cur.fetchall()
print(f"Encontrados {len(rows)} registros.")

if rows:
    ids = [r[0] for r in rows]
    print(f"IDs para excluir: {ids}")
    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(f"DELETE FROM historico_relatorio_consolidado WHERE id IN ({placeholders})", ids)
    print(f"Linhas afetadas: {cur.rowcount}")
    conn.commit()
    print("Exclusao concluida com sucesso!")
else:
    print("Nenhum registro para excluir.")

cur.close()
conn.close()
