import urllib.request
import json

url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
print("🔍 Testando a API de despesas...")

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    print("✅ Resposta recebida!")
    print(f"\n📊 Chaves: {list(data.keys())}")
    
    if data.get("erro"):
        print(f"❌ Erro retornado pela API: {data.get('mensagem')}")
    else:
        print(f"✅ Sem erro!")
    
    # Mostra um resumo
    if "atual" in data and data["atual"]:
        print(f"\n📊 Dados atuais: {list(data['atual'].keys()) if isinstance(data['atual'], dict) else type(data['atual'])}")
    
    # Mostra o JSON completo (primeiros 2000 caracteres)
    print("\n📄 JSON completo (primeiros 2000 chars):")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    
except Exception as e:
    print(f"❌ Erro ao chamar a API: {e}")
