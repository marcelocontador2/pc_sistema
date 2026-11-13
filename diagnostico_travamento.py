import psycopg2
import os

print("="*60)
print("🔍 DIAGNÓSTICO DE TRAVAMENTO")
print("="*60)

# 1. Testar conexão com o PostgreSQL
print("\n1. TESTANDO CONEXÃO COM O POSTGRESQL...")
try:
    conn = psycopg2.connect(host="localhost", port=5433, database="pc_database", user="postgres", password="pc_admin_2026")
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("   ✅ PostgreSQL respondeu corretamente!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ ERRO no PostgreSQL: {e}")

# 2. Verificar se o main.py tem erro de sintaxe
print("\n2. VERIFICANDO SINTAXE DO main.py...")
try:
    with open("pc_backend/main.py", "r", encoding="utf-8") as f:
        codigo = f.read()
    import ast
    ast.parse(codigo)
    print("   ✅ main.py está sintaticamente correto.")
except SyntaxError as e:
    print(f"   ❌ ERRO DE SINTAXE na linha {e.lineno}: {e.text}")
except Exception as e:
    print(f"   ❌ ERRO ao ler main.py: {e}")

# 3. Verificar se o servidor está rodando (tentando acessar a porta 9994)
print("\n3. VERIFICANDO SE O SERVIDOR ESTÁ RODANDO (porta 9994)...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
result = sock.connect_ex(('127.0.0.1', 9994))
if result == 0:
    print("   ✅ Servidor está rodando na porta 9994!")
else:
    print("   ❌ Servidor NÃO está rodando na porta 9994. Precisa reiniciar.")
sock.close()

# 4. Verificar se o HTML tem algum erro que possa travar
print("\n4. VERIFICANDO O HTML (relatorio_consolidado.html)...")
try:
    with open("pc_frontend/relatorio_consolidado.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Verifica se ainda tem 'undefined'
    if "undefined" in html.lower() and "data.faltando" not in html:
        print("   ⚠️ Pode haver 'undefined' no HTML. Vamos verificar...")
        for i, linha in enumerate(html.split("\n")):
            if "undefined" in linha.lower() and "total_faltando" in linha:
                print(f"      Linha {i+1}: {linha.strip()[:100]}")
    else:
        print("   ✅ HTML parece OK (sem undefined pendente).")
        
except Exception as e:
    print(f"   ❌ ERRO ao ler HTML: {e}")

print("\n" + "="*60)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("="*60)
