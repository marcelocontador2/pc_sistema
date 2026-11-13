import psycopg2

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()

    print("🔍 DIAGNÓSTICO PROFUNDO DO BANCO (POSTGRESQL):\n")
    
    # 1. Contagem simples de registros
    tabelas = ["balancete_linha", "documento_importado", "periodo"]
    for t in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"📌 Tabela '{t}': {count} registros.")
        
    print("\n" + "="*60)
    
    # 2. Vamos ver os documentos importados e seus períodos
    print("📄 ÚLTIMOS DOCUMENTOS IMPORTADOS:")
    cursor.execute("""
        SELECT d.id, d.periodo_id, p.descricao 
        FROM documento_importado d
        LEFT JOIN periodo p ON d.periodo_id = p.id
        LIMIT 5
    """)
    docs = cursor.fetchall()
    for d in docs:
        print(f" - Doc ID: {d[0]} | Periodo ID: {d[1]} | Nome Período: {d[2]}")
        
    print("\n" + "="*60)
    
    # 3. O Teste Crucial: Os balancetes estão ligados a algum documento?
    print("🔗 VÍNCULO ENTRE BALANCETE E DOCUMENTO:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM balancete_linha b
        LEFT JOIN documento_importado d ON b.documento_id = d.id
        WHERE d.id IS NULL
    """)
    orfaos = cursor.fetchone()[0]
    print(f" - Linhas de balancete SEM documento vinculado (órfãs): {orfaos}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM balancete_linha b
        JOIN documento_importado d ON b.documento_id = d.id
    """)
    vinculados = cursor.fetchone()[0]
    print(f" - Linhas de balancete COM documento vinculado: {vinculados}")

    print("\n" + "="*60)
    
    # 4. Se houver balancetes, vamos ver os primeiros 5 para entender o padrão
    print("🔎 AMOSTRA DE 5 LINHAS DO BALANCETE_LINHA:")
    cursor.execute("SELECT codigo_conta, descricao_conta, saldo_atual FROM balancete_linha LIMIT 5")
    amostras = cursor.fetchall()
    if amostras:
        for a in amostras:
            print(f" - Código: {a[0]} | Saldo: {a[2]} | Desc: {a[1]}")
    else:
        print(" ❌ A tabela balancete_linha está completamente VAZIA.")

    cursor.close()
    conn.close()
    print("\n✅ DIAGNÓSTICO CONCLUÍDO!")

except Exception as e:
    print(f"\n❌ ERRO DE CONEXÃO: {e}")
