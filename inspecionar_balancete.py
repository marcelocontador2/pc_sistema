import psycopg2

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()

    print("🔍 INSPECIONANDO OS DADOS REAIS DA TABELA BALANCETE_LINHA:\n")
    
    # 1. Vamos ver as primeiras 30 contas do período para entender o padrão dos códigos
    query = """
        SELECT b.codigo_conta, b.descricao_conta, b.saldo_atual, b.natureza_saldo, d.periodo
        FROM balancete_linha b
        JOIN documento_importado d ON b.documento_id = d.id
        WHERE d.periodo = '2026-TRIMESTRE-3'
        ORDER BY b.codigo_conta
        LIMIT 30;
    """
    cursor.execute(query)
    linhas = cursor.fetchall()
    
    if not linhas:
        print("❌ Nenhuma conta encontrada para o período '2026-TRIMESTRE-3'.")
        print("Buscando qualquer período disponível...")
        cursor.execute("SELECT DISTINCT periodo FROM documento_importado")
        periodos = cursor.fetchall()
        print("Períodos disponíveis no banco:", [p[0] for p in periodos])
    else:
        print(f"{'CÓDIGO':<15} | {'SALDO ATUAL':>15} | {'NAT.':<5} | DESCRIÇÃO")
        print("-" * 80)
        for l in linhas:
            codigo = l[0] if l[0] else ""
            desc = l[1][:40] if l[1] else ""
            saldo = float(l[2]) if l[2] else 0.0
            nat = l[3] if l[3] else ""
            print(f"{codigo:<15} | {saldo:>15,.2f} | {nat:<5} | {desc}")
            
        print("\n" + "="*60)
        print("🔍 TOTAIS POR CLASSE (Primeiro dígito do código):\n")
        cursor.execute("""
            SELECT SUBSTRING(b.codigo_conta FROM 1 FOR 1) as classe, 
                   COUNT(*), 
                   SUM(b.saldo_atual)
            FROM balancete_linha b
            JOIN documento_importado d ON b.documento_id = d.id
            WHERE d.periodo = '2026-TRIMESTRE-3'
            GROUP BY classe
            ORDER BY classe;
        """)
        totais = cursor.fetchall()
        for t in totais:
            print(f"Classe {t[0]}: {t[1]} contas | Soma dos saldos: R$ {float(t[2]):,.2f}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERRO: {e}")
