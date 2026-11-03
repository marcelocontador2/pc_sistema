import urllib.request
import json
import re

print("=" * 70)
print("COMPARANDO O JSON DO HISTÓRICO VS API NORMAL")
print("=" * 70)

# 1. Como o relatório busca os dados?
c = open(r"pc_frontend\relatorio_centro_custos_v2.html", encoding="utf-8-sig").read()
match_fetch = re.search(r'fetch\(([^)]+)\)', c)
if match_fetch:
    print(f"\n[1] O relatório busca dados nesta URL: {match_fetch.group(1)}")
else:
    print("\n[1] Não achei a chamada fetch no relatório.")

# 2. Como é o JSON do Histórico (ID 32)
print("\n[2] Testando a rota do Histórico: /historico_centro_custos/32")
try:
    req = urllib.request.Request("http://127.0.0.1:9994/historico_centro_custos/32")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("  Chaves principais:", list(data.keys()))
        if "dados" in data:
            print("  O objeto 'dados' é do tipo:", type(data["dados"]).__name__)
            if isinstance(data["dados"], dict):
                print("  Chaves dentro de 'dados':", list(data["dados"].keys()))
except Exception as e:
    print(f"  Erro ao buscar histórico: {e}")

# 3. Como é o JSON da API Normal (período 2026-TRIMESTRE-3)
print("\n[3] Testando a rota da API normal: /api/centro_custos/2026-TRIMESTRE-3")
try:
    req = urllib.request.Request("http://127.0.0.1:9994/api/centro_custos/2026-TRIMESTRE-3")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("  Chaves principais:", list(data.keys()))
except Exception as e:
    print(f"  Erro ao buscar API normal: {e}")
