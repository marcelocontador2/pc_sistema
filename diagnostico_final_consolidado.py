import psycopg2
import re

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

print("="*70)
print("🔍 DIAGNÓSTICO COMPLETO - RELATÓRIO CONSOLIDADO")
print("="*70)

# --- PARTE 1: Verificar BF no PostgreSQL ---
print("\n📊 [1/3] VERIFICANDO TABELA 'historico_analise_financeira_bf' NO POSTGRESQL...\n")
try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM historico_analise_financeira_bf")
    total = cursor.fetchone()[0]
    print(f"   Total de registros na tabela: {total}")
    
    # Todos os períodos
    cursor.execute("SELECT DISTINCT periodo FROM historico_analise_financeira_bf ORDER BY periodo")
    periodos = cursor.fetchall()
    print(f"   Períodos disponíveis:")
    for p in periodos:
        print(f"      - '{p[0]}'")
    
    # Testa o LIKE que o backend está usando
    print(f"\n   🧪 Testando busca com LIKE '%2026-TRIMESTRE-3%':")
    cursor.execute("SELECT id, periodo, data_geracao FROM historico_analise_financeira_bf WHERE periodo LIKE %s LIMIT 1", ('%2026-TRIMESTRE-3%',))
    row = cursor.fetchone()
    if row:
        print(f"      ✅ ENCONTRADO: ID={row[0]} | Período='{row[1]}' | Data={row[2]}")
    else:
        print(f"      ❌ NÃO ENCONTRADO com LIKE")
    
    # Testa busca exata
    print(f"\n   🧪 Testando busca exata '2026-TRIMESTRE-3':")
    cursor.execute("SELECT id, periodo FROM historico_analise_financeira_bf WHERE periodo = %s LIMIT 1", ('2026-TRIMESTRE-3',))
    row = cursor.fetchone()
    if row:
        print(f"      ✅ ENCONTRADO: ID={row[0]} | Período='{row[1]}'")
    else:
        print(f"      ❌ NÃO ENCONTRADO (busca exata)")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# --- PARTE 2: Verificar HTML ---
print("\n" + "="*70)
print("\n📄 [2/3] VERIFICANDO O HTML (relatorio_consolidado.html)...\n")
try:
    with open("pc_frontend/relatorio_consolidado.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    if "data.total_faltando" in html:
        print("   ❌ A variável 'data.total_faltando' ainda está no HTML (causa o undefined)")
        # Mostra o trecho
        for i, linha in enumerate(html.split("\n")):
            if "total_faltando" in linha:
                print(f"      Linha {i+1}: {linha.strip()[:150]}")
    else:
        print("   ✅ A variável 'data.total_faltando' NÃO está mais no HTML")
    
    if "data.faltando" in html and ".length" in html:
        print("   ✅ A variável 'data.faltando.length' está no HTML (correta)")
    else:
        print("   ⚠️ A variável 'data.faltando.length' pode não estar presente")
except Exception as e:
    print(f"   ❌ ERRO ao ler HTML: {e}")

# --- PARTE 3: Verificar main.py ---
print("\n" + "="*70)
print("\n🐍 [3/3] VERIFICANDO O BACKEND (main.py)...\n")
try:
    with open("pc_backend/main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
    
    if 'if chave == "analise_financeira_bf":' in main_content:
        print("   ✅ A condição 'if chave == \"analise_financeira_bf\":' está no código")
    else:
        print("   ❌ A condição 'if chave == \"analise_financeira_bf\":' NÃO está no código")
    
    if "LIKE %s" in main_content and "analise_financeira_bf" in main_content:
        print("   ✅ A query com LIKE está presente")
    else:
        print("   ⚠️ A query com LIKE pode não estar no lugar certo")
    
    if "total_faltando" in main_content:
        print("   ✅ O campo 'total_faltando' é retornado pelo backend")
    else:
        print("   ⚠️ O campo 'total_faltando' NÃO é retornado pelo backend")
except Exception as e:
    print(f"   ❌ ERRO ao ler main.py: {e}")

print("\n" + "="*70)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("="*70)
