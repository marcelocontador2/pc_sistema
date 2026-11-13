import ast
import subprocess
import time
import urllib.request
import json

print("="*70)
print("🔍 DIAGNÓSTICO FINAL DO RELATÓRIO CONSOLIDADO")
print("="*70)

# 1. Verificar sintaxe do main.py
print("\n[1/3] Verificando sintaxe do main.py...")
try:
    with open("pc_backend/main.py", "r", encoding="utf-8") as f:
        codigo = f.read()
    ast.parse(codigo)
    print("   ✅ Sintaxe do main.py está correta.")
except SyntaxError as e:
    print(f"   ❌ ERRO DE SINTAXE na linha {e.lineno}: {e.text}")
    exit()

# 2. Iniciar o servidor em background para testar
print("\n[2/3] Iniciando servidor temporário para teste...")
process = subprocess.Popen(
    [r".\pc_venv\Scripts\uvicorn.exe", "pc_backend.main:app", "--host", "127.0.0.1", "--port", "9999"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(5)  # Aguarda o servidor subir

# 3. Testar a rota /historico_relatorio_consolidado
print("\n[3/3] Testando rota /historico_relatorio_consolidado...")
try:
    req = urllib.request.Request("http://127.0.0.1:9999/historico_relatorio_consolidado")
    with urllib.request.urlopen(req, timeout=10) as response:
        status = response.status
        body = response.read().decode("utf-8")
        print(f"   Status HTTP: {status}")
        print(f"   Resposta: {body[:500]}")
        
        if status == 200:
            print("\n   ✅ A rota respondeu com sucesso!")
        else:
            print(f"\n   ❌ A rota retornou status {status}.")
except urllib.error.HTTPError as e:
    print(f"   ❌ ERRO HTTP {e.code}: {e.reason}")
    print(f"   Corpo do erro: {e.read().decode('utf-8')[:1000]}")
except Exception as e:
    print(f"   ❌ ERRO DE CONEXÃO: {e}")

# Para o servidor
process.terminate()
process.wait()

print("\n" + "="*70)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("="*70)
