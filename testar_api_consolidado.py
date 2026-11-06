import requests, json

url = "http://127.0.0.1:9994/api/relatorio_consolidado/2026-TRIMESTRE-3"
try:
    r = requests.get(url, timeout=10)
    print("Status:", r.status_code)
    data = r.json()
    
    print("\n=== MÓDULOS ENCONTRADOS ===")
    for chave, mod in data.get("encontrados", {}).items():
        print(f"✓ {mod['nome']} - {mod['data_geracao']}")
    
    print("\n=== MÓDULOS FALTANDO ===")
    for mod in data.get("faltando", []):
        print(f"✗ {mod['nome']}")
    
    print(f"\nTotal: {data.get('total_encontrados')} encontrados, {data.get('total_faltando')} faltando")
    
except Exception as e:
    print("Erro:", e)
