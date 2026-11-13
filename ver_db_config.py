import re

caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

# Encontra todos os DB_CONFIG no arquivo
matches = list(re.finditer(r'DB_CONFIG\s*=\s*\{[^}]+\}', content))
print(f"🔍 Encontrados {len(matches)} blocos DB_CONFIG no main.py:\n")
for i, m in enumerate(matches):
    linha = content[:m.start()].count('\n') + 1
    print(f"--- Bloco {i+1} (linha {linha}) ---")
    print(m.group(0))
    print()

# Procura também por funções helper de conexão
print("=" * 80)
print("🔍 Funções de conexão encontradas:")
print("=" * 80)
for nome in ["get_db_connection", "get_conn", "get_cursor", "conectar_db", "db_connect"]:
    if nome in content:
        print(f"   ✅ Função '{nome}' existe no arquivo.")
    else:
        print(f"   ❌ Função '{nome}' não existe.")
