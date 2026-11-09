import sqlite3
import json

db_path = r"pc_storage\banco_dados.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== AUDITORIA COMPLETA ===")

# 1. Verificar observacoes no banco
print("\n1. OBSERVACOES NO BANCO:")
cursor.execute("SELECT id, relatorio_id, item, texto FROM observacoes_consolidado")
rows = cursor.fetchall()
if not rows:
    print("   [VAZIO] Nenhuma observacao no banco.")
else:
    for r in rows:
        print(f"   ID: {r[0]} | Relatorio ID: {r[1]} | Item: {r[2]} | Texto: {r[3][:50]}...")

# 2. Verificar se o backend tem a rota
print("\n2. VERIFICANDO ROTA NO BACKEND:")
import subprocess
result = subprocess.run(["findstr", "/C:api/observacoes_consolidado", "pc_backend\\main.py"], capture_output=True, text=True)
if result.stdout:
    print("   [OK] Rota encontrada no main.py:")
    print("   " + result.stdout.strip().replace("\n", "\n   "))
else:
    print("   [ERRO] Rota NAO encontrada no main.py!")

# 3. Verificar se o frontend tem o modal
print("\n3. VERIFICANDO MODAL NO FRONTEND:")
with open(r"pc_frontend\relatorio_consolidado.html", "r", encoding="utf-8") as f:
    html = f.read()
if 'id="modal-obs"' in html:
    print("   [OK] Modal encontrado no HTML.")
else:
    print("   [ERRO] Modal NAO encontrado no HTML!")

if 'XMLHttpRequest' in html:
    print("   [OK] XMLHttpRequest encontrado no HTML.")
else:
    print("   [ERRO] XMLHttpRequest NAO encontrado no HTML!")

# 4. Verificar se o backend esta rodando
print("\n4. VERIFICANDO SERVIDOR:")
import urllib.request
try:
    response = urllib.request.urlopen("http://127.0.0.1:9994/api/observacoes_consolidado/22", timeout=3)
    data = response.read().decode()
    print(f"   [OK] Servidor respondendo. Resposta: {data}")
except Exception as e:
    print(f"   [ERRO] Servidor nao respondeu: {e}")

conn.close()
print("\n=== FIM DA AUDITORIA ===")
