import re

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔍 PROCURANDO CONFIGURAÇÕES DE BANCO NO MAIN.PY:\n")
print("-" * 60)

for i, linha in enumerate(linhas):
    # Procura variáveis de conexão, psycopg2, postgres, etc.
    if re.search(r'(PG_CONFIG|DATABASE_URL|DB_CONFIG|psycopg2\.connect|create_engine|postgresql://|DB_HOST|DB_NAME)', linha, re.IGNORECASE):
        # Imprime as 3 linhas anteriores e a linha em si para contexto
        for j in range(max(0, i-3), min(len(linhas), i+2)):
            print(f"{j+1}: {linhas[j].rstrip()}")
        print("-" * 60)
