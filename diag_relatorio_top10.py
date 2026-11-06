import re

c = open(r"pc_frontend\relatorio_comparativo_despesas.html", encoding='utf-8').read()

print("=" * 70)
print("DIAGNÓSTICO DO RELATÓRIO")
print("=" * 70)

# Verifica se o tbody existe
if 'id="tabela-top10"' in c:
    print("[OK] <tbody id='tabela-top10'> existe no HTML")
else:
    print("[FALTA] <tbody id='tabela-top10'> NÃO existe no HTML")

# Verifica se o JS preenche o tbody
if 'at.detalhes' in c:
    print("[OK] O JS referencia 'at.detalhes'")
else:
    print("[FALTA] O JS NÃO referencia 'at.detalhes'")

# Verifica se o fetch usa a API correta
if '/api/comparativo_despesas_v2/' in c:
    print("[OK] O JS busca de /api/comparativo_despesas_v2/")
else:
    print("[FALTA] O JS NÃO busca da API")

# Verifica se o histórico existe
if '/historico_comparativo_despesas/' in c:
    print("[OK] O JS busca do histórico de despesas")
else:
    print("[INFO] O JS não busca do histórico (usa API direto)")

# Mostra o trecho onde o tbody é preenchido
idx = c.find('tabela-top10')
if idx != -1:
    print("\n--- TRECHO ONDE O TBODY É PREENCHIDO ---")
    print(c[idx-200:idx+800])
else:
    print("\n[ERRO] Não encontrei 'tabela-top10' no arquivo.")

# Verifica o backend (que arquivo ele abre)
c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
match = re.search(r'url = f"http://127\.0\.0\.1:9994/(relatorio_comparativo_despesas[^?"]*)', c_back)
if match:
    print(f"\n--- BACKEND ABRE: /{match.group(1)} ---")
