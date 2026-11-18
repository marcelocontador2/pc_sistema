import psycopg2

conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
cur = conn.cursor()

# 1. Total de registros
cur.execute("SELECT COUNT(*) FROM demonstracao_resumo;")
print(f"Total de registros na tabela: {cur.fetchone()[0]}")

# 2. Contas com duplicata (agrupadas por conta + periodo + ano)
cur.execute("""
    SELECT d.grupo_demonstrativo, p.ano, COUNT(*) as qtd
    FROM demonstracao_resumo d
    JOIN periodo p ON d.periodo_id = p.id
    GROUP BY d.grupo_demonstrativo, p.ano
    HAVING COUNT(*) > 1
    ORDER BY qtd DESC, d.grupo_demonstrativo
    LIMIT 30;
""")
rows = cur.fetchall()
print(f"\nContas com duplicata (agrupadas por conta + ano): {len(rows)}")
print(f"{'Conta':<45} {'Ano':>4} {'Qtd':>4}")
print("-" * 60)
for r in rows:
    print(f"{r[0]:<45} {r[1]:>4} {r[2]:>4}")

# 3. Total de duplicatas (registros que podem ser removidos)
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT (grupo_demonstrativo, periodo_id))
    FROM demonstracao_resumo;
""")
duplicatas = cur.fetchone()[0]
print(f"\nTotal de registros duplicados (podem ser removidos): {duplicatas}")

cur.close()
conn.close()
