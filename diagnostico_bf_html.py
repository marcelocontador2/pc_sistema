import re
import psycopg2

# --- PARTE 1: Inspecionar o HTML ---
print("🔍 INSPECIONANDO O HTML DO RELATÓRIO CONSOLIDADO...\n")
caminho_html = "pc_frontend/relatorio_consolidado.html"

try:
    with open(caminho_html, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Procura o trecho do texto que mostra os faltantes
    ocorrencias = re.findall(r'[^.]*?[Ff]altam[^.]*?\.[^<]*', html)
    for i, oc in enumerate(ocorrencias):
        if len(oc) < 300:
            print(f"Ocorrência {i+1}: {oc.strip()}")
    
    # Procura onde a variável 'faltando' é usada
    print("\n📍 Onde a variável 'faltando' aparece no HTML:")
    for i, linha in enumerate(html.split("\n")):
        if "faltando" in linha.lower() and ("length" in linha or "módulo" in linha.lower() or "modulo" in linha.lower()):
            print(f"Linha {i+1}: {linha.strip()[:200]}")
            
except Exception as e:
    print(f"❌ Erro ao ler HTML: {e}")

# --- PARTE 2: Verificar dados de BF no PostgreSQL ---
print("\n" + "="*60)
print("🔍 VERIFICANDO A TABELA 'historico_analise_financeira_bf' NO POSTGRESQL...\n")

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # Verifica se a tabela existe e tem dados
    cursor.execute("SELECT COUNT(*) FROM historico_analise_financeira_bf")
    total = cursor.fetchone()[0]
    print(f"Total de registros na tabela 'historico_analise_financeira_bf': {total}")
    
    # Mostra os períodos disponíveis
    cursor.execute("SELECT DISTINCT periodo FROM historico_analise_financeira_bf")
    periodos = cursor.fetchall()
    print(f"Períodos disponíveis: {[p[0] for p in periodos] if periodos else 'Nenhum'}")
    
    # Verifica especificamente para 2026-TRIMESTRE-3
    cursor.execute("SELECT COUNT(*) FROM historico_analise_financeira_bf WHERE periodo = '2026-TRIMESTRE-3'")
    qtd = cursor.fetchone()[0]
    print(f"Registros para 2026-TRIMESTRE-3: {qtd}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro ao acessar PostgreSQL: {e}")
