import urllib.request
import json

print("=" * 80)
print("🔍 1. Testando a LISTAGEM de históricos (GET):")
print("=" * 80)

url_lista = "http://127.0.0.1:9994/historico_comparativo_receitas"
try:
    with urllib.request.urlopen(url_lista, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"✅ Lista retornada: {len(data)} registros")
    for i, item in enumerate(data):
        print(f"   {i+1}. ID={item.get('id')} | Período={item.get('periodo')} | Data={item.get('data_geracao', item.get('criado_em'))}")
except Exception as e:
    print(f"❌ Erro ao listar: {e}")

print("\n" + "=" * 80)
print("🔍 2. Testando a rota de SALVAR (POST):")
print("=" * 80)

url_salvar = "http://127.0.0.1:9994/api/comparativo_receitas_v2/2026-TRIMESTRE-3/salvar"
try:
    req = urllib.request.Request(url_salvar, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"✅ Resposta do salvar: {data}")
except Exception as e:
    print(f"❌ Erro ao salvar: {e}")

print("\n" + "=" * 80)
print("🔍 3. Listando novamente após salvar:")
print("=" * 80)

try:
    with urllib.request.urlopen(url_lista, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    print(f"✅ Lista após salvar: {len(data)} registros")
    for i, item in enumerate(data):
        print(f"   {i+1}. ID={item.get('id')} | Período={item.get('periodo')} | Data={item.get('data_geracao', item.get('criado_em'))}")
except Exception as e:
    print(f"❌ Erro ao listar novamente: {e}")
