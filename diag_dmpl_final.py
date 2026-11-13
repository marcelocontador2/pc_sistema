import requests
import json
import re

print("=" * 70)
print("DIAGNÓSTICO PROFISSIONAL - DMPL (FINAL)")
print("=" * 70)

# 1) O que a API do DMPL retorna?
print("\n[1] API /historico_analise_dmpl:")
try:
    r = requests.get("http://localhost:9994/historico_analise_dmpl")
    print(f"  Status: {r.status_code}")
    dados = r.json()
    print(f"  Itens: {len(dados)}")
    if dados:
        print(f"  Chaves do primeiro item: {list(dados[0].keys())}")
        print(f"  Amostra do item: {json.dumps(dados[0], ensure_ascii=False)[:400]}")
except Exception as e:
    print(f"  ERRO: {e}")

# 2) O que a função exibirSelecionado faz hoje no frontend?
print("\n[2] Função exibirSelecionado no HTML:")
with open("pc_frontend/analise_dmpl.html", "r", encoding="utf-8") as f:
    html = f.read()

padrao = re.compile(r'async function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(html)
if match:
    print(match.group(0)[:1200])
else:
    print("  -> Não encontrada!")

# 3) O que a tabela de DMPL no banco tem?
print("\n[3] Tabela historico_analise_dmpl no banco:")
import psycopg2
conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
cursor = conn.cursor()
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'historico_analise_dmpl'")
    colunas = [row[0] for row in cursor.fetchall()]
    print(f"  Colunas: {colunas}")
except Exception as e:
    print(f"  Erro ao listar colunas: {e}")
conn.close()

# 4) O que a função salvar_analise_dmpl faz no backend?
print("\n[4] Função salvar_analise_dmpl no main.py:")
with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    main_py = f.read()

padrao2 = re.compile(r'async def salvar_analise_dmpl.*?(?=\n@app\.|\Z)', re.DOTALL)
match2 = padrao2.search(main_py)
if match2:
    print(match2.group(0)[:1000])
else:
    print("  -> Não encontrada!")

print("\n" + "=" * 70)
