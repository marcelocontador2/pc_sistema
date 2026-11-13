import psycopg2
PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}
conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute("SELECT id, periodo, data_geracao FROM historico_analise_dmpl ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
conn.close()
if rows:
    print("=== REGISTROS DMPL NO POSTGRESQL ===")
    for r in rows:
        print(f"ID: {r[0]} | Período: {r[1]} | Data: {r[2]}")
else:
    print("❌ Nenhum registro na tabela historico_analise_dmpl!")
    print("   O DMPL precisa ser salvo primeiro na tela /analise_dmpl")
