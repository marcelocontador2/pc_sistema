import os
import re

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Procura a rota que serve o HTML da tela
rota_html = re.search(r'@app\.get\("/analise_comparativo_despesas".*?\ndef\s+\w+\([^)]*\):', content, re.DOTALL)
if rota_html:
    print("✅ Rota HTML encontrada:")
    print(rota_html.group(0)[:200])
else:
    print("❌ Rota HTML NÃO encontrada no main.py")

# 2. Procura a rota que lista o histórico
rota_hist = re.search(r'@app\.get\("/historico_comparativo_despesas"\)\s*\ndef\s+\w+\([^)]*\):.*?(?=\n@|\ndef\s+\w+)', content, re.DOTALL)
if rota_hist:
    print("\n✅ Rota de histórico encontrada:")
    bloco = rota_hist.group(0)
    # Mostra as primeiras 30 linhas da função
    for linha in bloco.split("\n")[:30]:
        print("   " + linha)
else:
    print("\n❌ Rota de histórico NÃO encontrada")

# 3. Verifica se há conexão com SQLite ou PostgreSQL na rota de histórico
if "sqlite3.connect" in (rota_hist.group(0) if rota_hist else ""):
    print("\n⚠️ A rota de histórico ainda usa SQLite3.connect! Problema encontrado.")
elif "psycopg2.connect" in (rota_hist.group(0) if rota_hist else ""):
    print("\n✅ A rota de histórico usa psycopg2.connect (PostgreSQL).")
elif "get_db_connection" in (rota_hist.group(0) if rota_hist else ""):
    print("\n✅ A rota de histórico usa get_db_connection (helper).")
else:
    print("\n❓ Não foi possível determinar qual banco a rota usa.")

# 4. Procura por "banco_dados.db" (SQLite antigo) no arquivo inteiro
print("\n🔍 Referências ao SQLite antigo (banco_dados.db):")
linhas = content.split("\n")
for i, linha in enumerate(linhas):
    if "banco_dados.db" in linha and "sqlite3.connect" in linha:
        print(f"   Linha {i+1}: {linha.strip()[:120]}")

# 5. Verifica se o JS da tela tem a função carregarHistorico correta
html_path = "pc_frontend/analise_comparativo_despesas.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    print("\n📄 HTML da tela encontrado.")
    if "function carregarHistorico" in html:
        print("   ✅ Função carregarHistorico encontrada no HTML.")
    else:
        print("   ❌ Função carregarHistorico NÃO encontrada no HTML.")
    if "function verificar" in html:
        print("   ✅ Função verificar encontrada no HTML.")
    else:
        print("   ❌ Função verificar NÃO encontrada no HTML.")
else:
    print("\n❌ HTML da tela de despesas não encontrado.")
