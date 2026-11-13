import urllib.request
import json

url = "http://127.0.0.1:9994/api/comparativo_receitas_v2/2026-TRIMESTRE-3"

print("🔍 Testando a API...")
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    print("✅ Resposta recebida!")
    print(f"\n📊 Tipo de resposta: {type(data).__name__}")
    print(f"📊 Chaves: {list(data.keys())}")
    
    print(f"\n📊 orcado_total: {data.get('orcado_total')}")
    print(f"📊 realizado_total: {data.get('realizado_total')}")
    print(f"📊 percentual_total: {data.get('percentual_total')}")
    
    grupos = data.get("grupos")
    print(f"\n📊 grupos: {type(grupos).__name__}, {len(grupos) if isinstance(grupos, list) else 'N/A'}")
    if isinstance(grupos, list) and grupos:
        print(f"   Primeiro grupo: {grupos[0]}")
    
    anterior = data.get("anterior")
    print(f"\n📊 anterior: {type(anterior).__name__}")
    if isinstance(anterior, dict):
        print(f"   Chaves do anterior: {list(anterior.keys())}")
        print(f"   anterior.realizado_total: {anterior.get('realizado_total')}")
        print(f"   anterior.percentual_total: {anterior.get('percentual_total')}")
        grupos_ant = anterior.get("grupos")
        print(f"   anterior.grupos: {type(grupos_ant).__name__}, {len(grupos_ant) if isinstance(grupos_ant, list) else 'N/A'}")
    elif anterior is None:
        print("   anterior é None (período anterior não encontrado)")
    
    print("\n📄 JSON completo (primeiros 2000 caracteres):")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    
except Exception as e:
    print(f"❌ Erro: {e}")
