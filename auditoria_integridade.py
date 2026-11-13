import os

# 1. Verifica se o arquivo matriz_integridade.py existe na pasta pc_backend
caminho = "pc_backend/matriz_integridade.py"
if os.path.exists(caminho):
    print(f"✅ Arquivo {caminho} existe.")
else:
    print(f"❌ Arquivo {caminho} NÃO existe.")
    # Procura em outras pastas
    print("\n🔍 Procurando 'matriz_integridade' em todo o projeto:")
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ("pc_venv", ".git", "__pycache__")]
        for file in files:
            if "matriz_integridade" in file:
                print(f"   Encontrado: {os.path.join(root, file)}")

# 2. Verifica como o main.py importa esse módulo
print("\n🔍 Verificando a importação no main.py:")
with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()
for i, linha in enumerate(linhas):
    if "matriz_integridade" in linha:
        print(f"   Linha {i+1}: {linha.strip()}")

# 3. Verifica se a rota de integridade usa SQLite ou PostgreSQL
print("\n🔍 Verificando a rota /integridade no main.py:")
content = "".join(linhas)
import re
padrao = r'@app\.get\("/integridade".*?(?=\n@|\ndef\s+\w+)'
match = re.search(padrao, content, re.DOTALL)
if match:
    bloco = match.group(0)
    if "sqlite3.connect" in bloco:
        print("   ⚠️ A rota usa SQLite3.connect (precisa migrar para PostgreSQL).")
    elif "PG_CONFIG" in bloco or "psycopg2.connect" in bloco:
        print("   ✅ A rota usa PostgreSQL.")
    else:
        print("   ❓ Não foi possível identificar a conexão.")
    # Mostra as primeiras 20 linhas da rota
    print("\n   --- Trecho da rota ---")
    for linha in bloco.split("\n")[:20]:
        print("   " + linha)
else:
    print("   Rota /integridade não encontrada no main.py.")
