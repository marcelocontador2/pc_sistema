import re
import shutil

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

shutil.copy(caminho, caminho + ".bak_fix_despesas_pg_real")

# Substitui a função get_historico_comparativo_despesas por uma versão que usa o PG_CONFIG correto
nova_funcao = '''@app.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    PG_CONFIG = {
        "host": "localhost", "port": 5433,
        "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
    }
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, periodo, data_geracao, dados_json FROM historico_comparativo_despesas ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        
        resultado = []
        for r in rows:
            resultado.append({
                "id": r["id"],
                "periodo": r["periodo"],
                "data_geracao": r["data_geracao"],
                "dados": r["dados_json"]
            })
        return resultado
    except Exception as e:
        print(f"[ERRO] Falha ao buscar histórico de despesas: {e}")
        return []
'''

# Localiza e substitui a função
padrao = r'@app\.get\("/historico_comparativo_despesas"\)\s*\ndef\s+get_historico_comparativo_despesas\(\):.*?(?=\n@|\ndef\s+\w+)'
match = re.search(padrao, content, re.DOTALL)
if match:
    content = content[:match.start()] + nova_funcao + content[match.end():]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Função substituída com PG_CONFIG correto (porta 5433, senha pc_admin_2026).")
else:
    print("⚠️ Função não encontrada.")

# Verifica como ficou
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()
idx = content.find("def get_historico_comparativo_despesas")
if idx != -1:
    print("\n📋 Como ficou a função:")
    print("-" * 80)
    for linha in content[idx:idx+500].split("\n")[:20]:
        print("   " + linha)
