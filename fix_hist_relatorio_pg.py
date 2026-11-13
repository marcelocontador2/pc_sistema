import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_hist_relatorio_pg")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função get_hist_consolidado
idx_inicio = conteudo.find("async def get_hist_consolidado():")
if idx_inicio == -1:
    idx_inicio = conteudo.find("def get_hist_consolidado():")

if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''async def get_hist_consolidado():
    import json
    import psycopg2
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2], "dados": r[3]} for r in rows]
    except Exception as e:
        return []'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    print("✅ Função 'get_hist_consolidado' atualizada para PostgreSQL.")
else:
    print("❌ Função 'get_hist_consolidado' não encontrada.")

# Verifica sintaxe e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
