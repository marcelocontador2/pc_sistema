import re
import json
import requests
import psycopg2

print("=" * 70)
print("DIAGNÓSTICO PROFISSIONAL - DMPL")
print("=" * 70)

# ---------------------------------------------------------------
# 1) O que a função salvar_analise_dmpl faz no backend?
# ---------------------------------------------------------------
print("\n[1] FUNCAO salvar_analise_dmpl NO BACKEND:")
with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    main_py = f.read()

padrao = re.compile(r'async def salvar_analise_dmpl.*?(?=\n@app\.|\Z)', re.DOTALL)
match = padrao.search(main_py)
if match:
    print(match.group(0)[:1500])
else:
    print("  -> Funcao NAO encontrada!")

# ---------------------------------------------------------------
# 2) O que a funcao carregarHistorico espera no frontend?
# ---------------------------------------------------------------
print("\n[2] FUNCAO carregarHistorico NO FRONTEND:")
with open("pc_frontend/analise_dmpl.html", "r", encoding="utf-8") as f:
    html = f.read()

padrao2 = re.compile(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', re.DOTALL)
match2 = padrao2.search(html)
if match2:
    print(match2.group(0))
else:
    print("  -> Funcao NAO encontrada!")

# ---------------------------------------------------------------
# 3) O que o banco de dados tem na tabela historico_analise_dmpl?
# ---------------------------------------------------------------
print("\n[3] TABELA historico_analise_dmpl NO BANCO:")
PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}
conn = psycopg2.connect(**PG_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT id, periodo, dados FROM historico_analise_dmpl ORDER BY id DESC LIMIT 3")
rows = cursor.fetchall()
conn.close()

if rows:
    for row in rows:
        print(f"  ID: {row[0]} | Periodo: {row[1]}")
        print(f"  Dados: {'PREENCHIDO' if row[2] else 'NULL (vazio)'}")
        if row[2]:
            print(f"  Amostra: {json.dumps(row[2], ensure_ascii=False)[:150]}...")
else:
    print("  -> Tabela VAZIA (nenhum historico salvo).")

# ---------------------------------------------------------------
# 4) O que a rota /historico_analise_dmpl retorna agora?
# ---------------------------------------------------------------
print("\n[4] RESPOSTA DA API /historico_analise_dmpl:")
try:
    r = requests.get("http://localhost:9994/historico_analise_dmpl")
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        lista = r.json()
        print(f"  Itens retornados: {len(lista)}")
        if lista:
            print(f"  Chaves do primeiro item: {list(lista[0].keys())}")
    else:
        print(f"  Erro: {r.text[:200]}")
except Exception as e:
    print(f"  Erro de conexao: {e}")

# ---------------------------------------------------------------
# 5) O que a rota /historico_analise_bp (que funciona) retorna?
# ---------------------------------------------------------------
print("\n[5] RESPOSTA DA API /historico_analise_bp (para comparar):")
try:
    r = requests.get("http://localhost:9994/historico_analise_bp")
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        lista = r.json()
        print(f"  Itens retornados: {len(lista)}")
        if lista:
            print(f"  Chaves do primeiro item: {list(lista[0].keys())}")
    else:
        print(f"  Erro: {r.text[:200]}")
except Exception as e:
    print(f"  Erro de conexao: {e}")

print("\n" + "=" * 70)
