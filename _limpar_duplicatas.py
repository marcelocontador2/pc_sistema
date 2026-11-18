import psycopg2
import datetime

conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
cur = conn.cursor()

print("=" * 60)
print("LIMPEZA DE DUPLICATAS EM demonstracao_resumo")
print("=" * 60)

# 1. Contagem antes
cur.execute("SELECT COUNT(*) FROM demonstracao_resumo;")
antes = cur.fetchone()[0]
print(f"Registros antes: {antes}")

# 2. Remover duplicatas mantendo o mais recente por (conta, periodo_id)
cur.execute("""
    DELETE FROM demonstracao_resumo a
    USING demonstracao_resumo b
    WHERE a.id < b.id
      AND a.grupo_demonstrativo = b.grupo_demonstrativo
      AND a.periodo_id = b.periodo_id;
""")
removidos = cur.rowcount
print(f"Registros removidos: {removidos}")

# 3. Contagem depois
cur.execute("SELECT COUNT(*) FROM demonstracao_resumo;")
depois = cur.fetchone()[0]
print(f"Registros depois: {depois}")

# 4. Verificar se ainda ha duplicatas
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT (grupo_demonstrativo, periodo_id))
    FROM demonstracao_resumo;
""")
restantes = cur.fetchone()[0]
print(f"Duplicatas restantes: {restantes}")

# 5. Commit
conn.commit()
print("\nTransacao commitada.")

# 6. Verificar as contas que sobraram
cur.execute("""
    SELECT d.grupo_demonstrativo, p.ano, d.valor_atual
    FROM demonstracao_resumo d
    JOIN periodo p ON d.periodo_id = p.id
    ORDER BY p.ano DESC, d.grupo_demonstrativo
    LIMIT 20;
""")
print("\nPrimeiras 20 contas (apos limpeza):")
print(f"{'Conta':<40} {'Ano':>4} {'Valor':>15}")
print("-" * 65)
for r in cur.fetchall():
    print(f"{r[0]:<40} {r[1]:>4} {float(r[2]):>15,.2f}")

cur.close()
conn.close()
print("\nConcluido.")
