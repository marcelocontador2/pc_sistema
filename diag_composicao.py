import requests
import re
import psycopg2
import json

print("=" * 70)
print("DIAGNÓSTICO PROFISSIONAL - COMPOSIÇÃO RECEITAS/DESPESAS")
print("=" * 70)

# 1) O que o Frontend está chamando?
print("\n[1] FUNÇÕES DO FRONTEND (composicao_receitas_despesas.html):")
with open("pc_frontend/composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

# Lista as funcoes
for m in re.finditer(r'async function (\w+)', html):
    print(f"  - {m.group(1)}")

# Lista os fetches
fetches = re.findall(r"fetch\([\'\"]([^\'\"]+)", html)
print("\n  Rotas chamadas no Frontend:")
for f in set(fetches):
    print(f"  - {f}")

# 2) O que o Backend tem?
print("\n[2] ROTAS NO BACKEND (main.py):")
with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    main_py = f.read()

for m in re.finditer(r'@app\.(get|post)\("([^"]*composicao[^"]*)"\)', main_py, re.IGNORECASE):
    print(f"  - {m.group(1).upper()} {m.group(2)}")
for m in re.finditer(r'@app\.(get|post)\("([^"]*receitas_despesas[^"]*)"\)', main_py, re.IGNORECASE):
    print(f"  - {m.group(1).upper()} {m.group(2)}")

# 3) O banco tem dados?
print("\n[3] TABELAS NO BANCO (PostgreSQL):")
try:
    conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%composicao%' OR table_name LIKE '%receitas_despesas%'")
    tabelas = [r[0] for r in cur.fetchall()]
    print(f"  Tabelas encontradas: {tabelas}")
    
    for t in tabelas:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  - {t}: {count} registros")
    conn.close()
except Exception as e:
    print(f"  Erro ao conectar no banco: {e}")

# 4) A API está respondendo?
print("\n[4] TESTANDO AS ROTAS DA API:")
for rota in set(fetches):
    if rota.startswith('/api/') or rota.startswith('/historico_'):
        try:
            r = requests.get(f"http://localhost:9994{rota}")
            print(f"  GET {rota}: Status {r.status_code}")
            if r.status_code != 200:
                print(f"    Resposta: {r.text[:100]}")
        except Exception as e:
            print(f"  GET {rota}: Erro de conexao")

print("\n" + "=" * 70)
