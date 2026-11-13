import re

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Verifica as rotas de Exibir, PDF e Excluir de despesas
rotas_para_verificar = [
    "/historico_comparativo_despesas/{id}",
    "/gerar_pdf_comparativo_despesas/{id}",
    "/gerar_pdf_comparativo_despesas",
    "/excluir_multiplos_comparativo_despesas",
    "/api/comparativo_despesas_v2/{periodo}/salvar",
]

print("=" * 80)
print("🔍 Verificando rotas de despesas no backend:")
print("=" * 80)

for rota in rotas_para_verificar:
    # Procura a rota no arquivo
    encontrada = False
    for i, linha in enumerate(content.split("\n")):
        if rota in linha and "@app." in linha:
            print(f"✅ {rota} → Linha {i+1}: {linha.strip()[:120]}")
            encontrada = True
            break
    if not encontrada:
        print(f"❌ {rota} NÃO encontrada!")

# 2. Para as rotas encontradas, verifica se usam SQLite ou PostgreSQL
print("\n" + "=" * 80)
print("🔍 Verificando se as rotas usam SQLite ou PostgreSQL:")
print("=" * 80)

# Procura o bloco de cada rota e verifica a conexão
def extrair_funcao(nome_rota):
    idx = content.find(nome_rota)
    if idx == -1:
        return None
    # Encontra a próxima rota ou fim
    proximo = content.find("@app.", idx + 10)
    if proximo == -1:
        proximo = len(content)
    return content[idx:proximo]

for rota in ["/historico_comparativo_despesas/{id}", "/gerar_pdf_comparativo_despesas", "/excluir_multiplos_comparativo_despesas"]:
    bloco = extrair_funcao(rota)
    if bloco:
        if "sqlite3.connect" in bloco:
            print(f"⚠️ {rota}: usa SQLite3.connect (PRECISA CORRIGIR)")
        elif "PG_CONFIG" in bloco:
            print(f"✅ {rota}: usa PG_CONFIG (PostgreSQL) - OK")
        elif "DB_CONFIG" in bloco:
            print(f"⚠️ {rota}: usa DB_CONFIG (senha errada) - PRECISA CORRIGIR")
        else:
            print(f"❓ {rota}: não foi possível identificar a conexão")

# 3. Verifica se o Playwright está sendo usado no PDF
print("\n" + "=" * 80)
print("🔍 Verificando a rota de PDF:")
print("=" * 80)
bloco_pdf = extrair_funcao("/gerar_pdf_comparativo_despesas")
if bloco_pdf:
    if "playwright" in bloco_pdf.lower():
        print("   ✅ Usa Playwright para gerar o PDF.")
    else:
        print("   ⚠️ NÃO usa Playwright. Pode estar quebrado.")
    if "historico_id" in bloco_pdf:
        print("   ✅ Aceita historico_id.")
    else:
        print("   ⚠️ NÃO aceita historico_id. Precisa ser corrigido.")
