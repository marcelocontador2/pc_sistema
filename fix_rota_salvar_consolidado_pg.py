import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_salvar_consolidado_pg")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a rota de salvar relatório consolidado
idx_inicio = conteudo.find('@app.post("/salvar_relatorio_consolidado/{periodo}")')
if idx_inicio != -1:
    # Encontra o final da função (próxima @app ou fim do arquivo)
    idx_fim = conteudo.find('@app.', idx_inicio + 10)
    if idx_fim == -1:
        idx_fim = len(conteudo)
    
    nova_funcao = '''@app.post("/salvar_relatorio_consolidado/{periodo}")
async def salvar_relatorio_consolidado_novo(periodo: str):
    import json
    from datetime import datetime
    import psycopg2
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        # 1. Coleta os dados de todos os módulos no PostgreSQL
        dados_api = await api_relatorio_consolidado_novo(periodo)
        
        if dados_api.get("status") == "faltando" and len(dados_api.get("faltando", [])) > 0:
            return {
                "ok": False,
                "mensagem": f"Faltam {len(dados_api['faltando'])} módulo(s) para consolidar.",
                "faltando": dados_api["faltando"]
            }
        
        dados_consolidados = {
            "periodo": periodo,
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "dados": dados_api.get("encontrados", [])
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Salva no PostgreSQL
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
                id SERIAL PRIMARY KEY,
                periodo TEXT,
                data_geracao TEXT,
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_consolidados, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Relatório salvo com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[idx_fim:]
    print("✅ Rota de salvar relatório consolidado atualizada para PostgreSQL!")
else:
    print("❌ Rota de salvar não encontrada no main.py.")

# Verifica sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
