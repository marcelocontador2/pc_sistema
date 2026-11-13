import shutil

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_pg_config_error")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função api_integridade_matriz_calcular
idx_inicio = conteudo.find('async def api_integridade_matriz_calcular(periodo: str):')
if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    # Substitui a função inteira, garantindo que o PG_CONFIG seja definido dentro dela
    nova_funcao = '''async def api_integridade_matriz_calcular(periodo: str):
    import json
    import psycopg2
    
    # Definição local para garantir que a variável exista no escopo
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        # Tenta primeiro buscar o último histórico salvo no PostgreSQL
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado_json FROM historico_integridade_matriz ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            # Se encontrou histórico, retorna exatamente o JSON salvo
            return json.loads(row[0])
            
        # Se não encontrou, tenta calcular via CSVs (fallback)
        from .matriz_integridade import gerar_matriz
        dados = gerar_matriz(periodo)
        return dados
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ Erro do PG_CONFIG corrigido: a variável agora é definida dentro da função!")
else:
    print("❌ Função 'api_integridade_matriz_calcular' não encontrada no main.py.")
