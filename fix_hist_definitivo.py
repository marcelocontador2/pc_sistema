import ast
import shutil
import re

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_hist_definitivo")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

print("🔍 Localizando todas as definições de 'get_hist_consolidado'...")

# Remove TODAS as versões antigas da função (da rota até o próximo @app ou def)
padrao = r'(@app\.get\("/historico_relatorio_consolidado"\)\s*)?(async\s+)?def get_hist_consolidado\(\):.*?(?=\n@app\.|\n@\w|\ndef |\Z)'
conteudo, count = re.subn(padrao, '', conteudo, flags=re.DOTALL)

if count > 0:
    print(f"✅ {count} versão(ões) antiga(s) removida(s).")
else:
    print("⚠️ Nenhuma versão antiga encontrada com o padrão. Tentando abordagem alternativa...")
    # Abordagem alternativa: remover linha por linha
    linhas = conteudo.split("\n")
    novas_linhas = []
    pular = False
    for linha in linhas:
        if '@app.get("/historico_relatorio_consolidado")' in linha:
            pular = True
            continue
        if pular and ('def ' in linha or '@app.' in linha) and 'get_hist_consolidado' not in linha:
            pular = False
        if not pular:
            novas_linhas.append(linha)
    conteudo = "\n".join(novas_linhas)
    print("✅ Remoção via abordagem alternativa concluída.")

# Adiciona a versão correta no final do arquivo
nova_funcao = '''

@app.get("/historico_relatorio_consolidado")
async def get_hist_consolidado():
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
        return []
'''

conteudo += nova_funcao
print("✅ Nova função 'get_hist_consolidado' adicionada.")

# Verifica a sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
