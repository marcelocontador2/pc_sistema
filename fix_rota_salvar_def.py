import shutil

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_rota_salvar")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garante que a rota de salvar existe e está correta
if '@app.post("/api/integridade_matriz/{periodo}/salvar")' not in conteudo:
    print("⚠️ Rota de salvar ausente. Reinserindo...")
    # Procura a definição da função de salvar para inserir a rota logo acima
    idx_func = conteudo.find('async def salvar_integridade_matriz(periodo: str, request: Request):')
    if idx_func != -1:
        rota = '@app.post("/api/integridade_matriz/{periodo}/salvar")\n'
        conteudo = conteudo[:idx_func] + rota + conteudo[idx_func:]

# 2. Garante que a função de salvar tem o PG_CONFIG e está completa
idx_inicio = conteudo.find('async def salvar_integridade_matriz(periodo: str, request: Request):')
if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''async def salvar_integridade_matriz(periodo: str, request: Request):
    import json
    from datetime import datetime
    import psycopg2
    
    # Definição local para garantir que a variável exista no escopo
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        body = await request.json()
        matriz = body.get("matriz", [])
        justificativas = body.get("justificativas", {})
        
        dados_matriz = {
            "periodo": periodo,
            "matriz": matriz,
            "justificativas": justificativas
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Garante que a tabela exista no Postgres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
                id SERIAL PRIMARY KEY, 
                periodo TEXT, 
                data_geracao TEXT, 
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Matriz salva com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    print("✅ Função de salvar atualizada com PG_CONFIG local.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ main.py corrigido! A rota de salvar foi restaurada.")
