import psycopg2

conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
cur = conn.cursor()

# 1. Total de registros por ano
cur.execute("""
    SELECT p.ano, COUNT(*)
    FROM demonstracao_resumo d
    JOIN periodo p ON d.periodo_id = p.id
    GROUP BY p.ano
    ORDER BY p.ano DESC;
""")
print("Registros por ano:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} registros")

# 2. Total de registros por periodo
cur.execute("""
    SELECT p.ano, p.periodo_acumulado, COUNT(*)
    FROM demonstracao_resumo d
    JOIN periodo p ON d.periodo_id = p.id
    GROUP BY p.ano, p.periodo_acumulado
    ORDER BY p.ano DESC, p.periodo_acumulado;
""")
print("\nRegistros por periodo:")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]}): {r[2]} registros")

# 3. Contas do BP (Ativo/Passivo/PL)
cur.execute("""
    SELECT d.grupo_demonstrativo, p.ano, d.valor_atual
    FROM demonstracao_resumo d
    JOIN periodo p ON d.periodo_id = p.id
    WHERE d.grupo_demonstrativo IN (
        'Ativo Circulante', 'Ativo Nao Circulante',
        'Passivo Circulante', 'Passivo Nao Circulante',
        'Patrimonio Liquido', 'Total Geral'
    )
    ORDER BY p.ano DESC, d.grupo_demonstrativo;
""")
print("\nContas do BP (por ano):")
print(f"{'Conta':<35} {'Ano':>4} {'Valor':>18}")
print("-" * 60)
for r in cur.fetchall():
    print(f"{r[0]:<35} {r[1]:>4} {float(r[2]):>18,.2f}")

cur.close()
conn.close()
