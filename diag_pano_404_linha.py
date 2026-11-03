import re
import urllib.request
import json

print("=" * 70)
print("DIAGNÓSTICO: ERRO 404 NO PANORAMA (LINHA 1087)")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
linhas = c_back.splitlines()

# 1. Mostra o contexto da linha 1087
print("\n--- CONTEXTO DA LINHA 1087 ---")
for i in range(max(0, 1080), min(len(linhas), 1095)):
    prefixo = ">>" if i == 1086 else "  "
    print(f"{prefixo} {i+1}: {linhas[i]}")

# 2. Testa a rota da API do Panorama que a tela chama
print("\n--- TESTANDO A ROTA /api/panorama/2026-TRIMESTRE-3 ---")
try:
    url = "http://127.0.0.1:9994/api/panorama/2026-TRIMESTRE-3"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        print(f"Status HTTP: {status}")
        print(f"Resposta (primeiros 200 chars): {response.read().decode('utf-8')[:200]}")
except Exception as e:
    print(f"Erro na requisição: {e}")

# 3. Verifica a rota /panorama
print("\n--- TESTANDO A ROTA /panorama ---")
try:
    url = "http://127.0.0.1:9994/panorama"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        print(f"Status HTTP: {response.getcode()}")
except Exception as e:
    print(f"Erro na requisição: {e}")
