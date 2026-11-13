import urllib.request
import json

print("🔍 Testando Exibir com ID real (12):")
try:
    with urllib.request.urlopen("http://127.0.0.1:9994/historico_comparativo_despesas/12", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    print(f"✅ Status: 200")
    print(f"Chaves: {list(data.keys())}")
    print(f"erro: {data.get('erro')}")
    
    if data.get('dados'):
        dados = data['dados']
        if isinstance(dados, str):
            dados = json.loads(dados)
        print(f"\n📊 Estrutura do 'dados':")
        print(f"   Chaves: {list(dados.keys()) if isinstance(dados, dict) else type(dados)}")
        if isinstance(dados, dict):
            if 'atual' in dados:
                print(f"   ✅ Tem 'atual'!")
                print(f"   atual.grupos: {len(dados['atual'].get('grupos', []))} itens")
                print(f"   atual.empenhado_total: {dados['atual'].get('empenhado_total')}")
            else:
                print(f"   ⚠️ NÃO tem 'atual'. Estrutura: {json.dumps(dados, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"⚠️ 'dados' está vazio ou ausente.")
        print(f"   JSON completo: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
except Exception as e:
    print(f"❌ Erro: {e}")
