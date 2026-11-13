import re

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Encontra a rota de "relatorios_importados" (que funciona) e mostra como ela conecta
print("=" * 80)
print("🔍 Como a rota /api/relatorios_importados (que funciona) conecta no banco?")
print("=" * 80)

padrao = r'@app\.get\("/api/relatorios_importados"\).*?(?=\n@|\ndef\s+\w+)'
match = re.search(padrao, content, re.DOTALL)
if match:
    bloco = match.group(0)
    # Mostra as primeiras 30 linhas
    for linha in bloco.split("\n")[:30]:
        print("   " + linha)
else:
    print("   Rota não encontrada.")

# 2. Procura por qualquer conexão psycopg2 no arquivo
print("\n" + "=" * 80)
print("🔍 Todas as chamadas a psycopg2.connect no arquivo:")
print("=" * 80)
for i, linha in enumerate(content.split("\n")):
    if "psycopg2.connect" in linha:
        print(f"   Linha {i+1}: {linha.strip()[:150]}")

# 3. Procura por variáveis de ambiente relacionadas a banco
print("\n" + "=" * 80)
print("🔍 Variáveis de ambiente ou imports relacionados a banco:")
print("=" * 80)
for i, linha in enumerate(content.split("\n")):
    if "os.environ" in linha and ("DB" in linha or "PG" in linha or "POSTGRES" in linha):
        print(f"   Linha {i+1}: {linha.strip()[:150]}")
    if "dotenv" in linha.lower():
        print(f"   Linha {i+1}: {linha.strip()[:150]}")
