import urllib.request
import json

print("=" * 80)
print("🔍 Testando as rotas do Comparativo de Despesas:")
print("=" * 80)

rotas = [
    ("GET", "http://127.0.0.1:9994/historico_comparativo_despesas"),
    ("GET", "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"),
]

for metodo, url in rotas:
    print(f"\n📡 Testando {metodo} {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        if isinstance(data, list):
            print(f"   ✅ Retornou lista com {len(data)} itens")
            if data and len(data) > 0:
                print(f"   Primeiro item: {data[0]}")
        elif isinstance(data, dict):
            if data.get("erro"):
                print(f"   ❌ Erro: {data.get('mensagem')}")
            else:
                print(f"   ✅ Retornou dict com chaves: {list(data.keys())}")
                print(f"   Campos: realizado_total={data.get('realizado_total')}, grupos={len(data.get('grupos', []))}")
        else:
            print(f"   ✅ Retornou: {type(data)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

# Verifica se a rota de salvar existe
print(f"\n📡 Testando POST /api/comparativo_despesas_v2/2026-TRIMESTRE-3/salvar")
try:
    req = urllib.request.Request(
        "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3/salvar",
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"   ✅ Retornou: {data}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
