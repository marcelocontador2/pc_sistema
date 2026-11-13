import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_hist_consolidado_coluna")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função get_hist_consolidado
idx_inicio = conteudo.find("async def get_hist_consolidado():")
if idx_inicio == -1:
    # Tenta sem async
    idx_inicio = conteudo.find("def get_hist_consolidado():")

if idx_inicio != -1:
    i = conteudo.find("{", idx_inicio)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    # A rota original chama "SELECT id, periodo, data_geracao FROM historico_relatorio_consolidado"
    # mas tenta acessar r[3] (resultado_json). Vamos corrigir a consulta para trazer a coluna resultado_json.
    nova_funcao = '''async def get_hist_consolidado():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2], "dados": r[3]} for r in rows]'''
    
    conteudo = conteudo[:idx_inicio] + nova_funcao + conteudo[i:]
    print("✅ Função 'get_hist_consolidado' corrigida para trazer a coluna resultado_json.")
else:
    print("❌ Função 'get_hist_consolidado' não encontrada no main.py.")

# Verifica sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
