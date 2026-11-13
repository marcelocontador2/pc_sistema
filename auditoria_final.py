import psycopg2

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()

    print("🔍 COLUNAS DA TABELA 'periodo':")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'periodo'
        ORDER BY ordinal_position
    """)
    for c in cursor.fetchall():
        print(f"   - {c[0]} ({c[1]})")

    print("\n🔍 AMOSTRA DE DADOS DA TABELA 'periodo' (todas as colunas):")
    cursor.execute("SELECT * FROM periodo LIMIT 5")
    colunas = [desc[0] for desc in cursor.description]
    print("Colunas retornadas:", colunas)
    for row in cursor.fetchall():
        print("   ", row)

    print("\n" + "="*60)
    print("🔍 VÍNCULOS REAIS: DOCUMENTO -> BALANCETE")
    cursor.execute("""
        SELECT d.id, d.periodo_id, COUNT(b.id) as qtd_linhas
        FROM documento_importado d
        LEFT JOIN balancete_linha b ON b.documento_id = d.id
        GROUP BY d.id, d.periodo_id
        HAVING COUNT(b.id) > 0
        ORDER BY qtd_linhas DESC
        LIMIT 10
    """)
    print("(Mostrando apenas documentos que têm balancetes vinculados)")
    for row in cursor.fetchall():
        print(f"   Doc: {row[0]} | Periodo_ID: {row[1]} | Qtd Linhas: {row[2]}")

    print("\n" + "="*60)
    print("🔍 TOTAIS POR CLASSE (usando apenas balancete_linha, sem JOINs):")
    cursor.execute("""
        SELECT SUBSTRING(codigo_conta FROM 1 FOR 1) as classe,
               COUNT(*) as qtd,
               SUM(saldo_atual) as total
        FROM balancete_linha
        WHERE codigo_conta IS NOT NULL
        GROUP BY classe
        ORDER BY classe
    """)
    for row in cursor.fetchall():
        total = float(row[2]) if row[2] else 0.0
        print(f"   Classe {row[0]}: {row[1]} contas | Total: R$ {total:,.2f}")

    print("\n" + "="*60)
    print("🔍 AMOSTRA REAL DE LINHAS DO BALANCETE (10 primeiras):")
    cursor.execute("SELECT codigo_conta, descricao_conta, saldo_atual, documento_id FROM balancete_linha LIMIT 10")
    for row in cursor.fetchall():
        saldo = float(row[2]) if row[2] else 0.0
        print(f"   {row[0]:<15} | {saldo:>15,.2f} | {str(row[1])[:40]:<40} | Doc: {row[3]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERRO: {e}")
