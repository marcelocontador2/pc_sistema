import urllib.request
import json

url = f"http://127.0.0.1:9994/historico_comparativo_receitas"
print("🔍 Buscando lista de históricos...")

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    print(f"\n✅ Total de históricos retornados pela API: {len(data)}")
    print("-" * 80)
    for i, item in enumerate(data):
        id_ = item.get('id')
        periodo = item.get('periodo')
        data_geracao = item.get('data_geracao') or item.get('criado_em')
        print(f"   {i+1}. ID={id_} | Período={periodo} | Data={data_geracao}")
    print("-" * 80)
except Exception as e:
    print(f"❌ Erro ao buscar: {e}")
