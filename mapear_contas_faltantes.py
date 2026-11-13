import psycopg2

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()

    print("🔍 MAPEANDO OS CÓDIGOS REAIS DAS CONTAS FALTANTES:\n")

    termos = [
        "VALORES RESTITUÍVEIS",
        "RECEITA CORRENTE",
        "DESPESAS CORRENTES",
        "CRÉDITO EMPENHADO",
        "RP NÃO PROCESSADOS",
        "INCORPORAÇÃO DE ATIVOS",
        "CRÉDITO EMPENHADO LIQUIDADO"
    ]

    for termo in termos:
        print(f"🔎 BUSCANDO: '{termo}'")
        cursor.execute("""
            SELECT codigo_conta, descricao_conta, saldo_atual 
            FROM balancete_linha 
            WHERE descricao_conta ILIKE %s
            ORDER BY codigo_conta
            LIMIT 5
        """, (f"%{termo}%",))
        resultados = cursor.fetchall()
        
        if resultados:
            for r in resultados:
                saldo = float(r[2]) if r[2] else 0.0
                print(f"   ✓ Código: {r[0]:<15} | Saldo: R$ {saldo:>15,.2f} | Desc: {r[1][:50]}")
        else:
            print("   ❌ Nenhuma conta encontrada com esse termo.")
        print("-" * 60)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERRO: {e}")
