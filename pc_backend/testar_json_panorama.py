import requests, json

# Busca a lista de históricos
r = requests.get('http://127.0.0.1:9994/historico_panorama')
historicos = r.json()

if not historicos:
    print("Nenhum histórico encontrado.")
else:
    # Pega o primeiro ID
    id_teste = historicos[0]['id']
    print(f"Testando ID: {id_teste}")
    
    # Busca os dados do histórico
    r2 = requests.get(f'http://127.0.0.1:9994/historico_panorama/{id_teste}')
    dados = r2.json()
    
    print("\n=== ESTRUTURA DO JSON ===")
    print(json.dumps(dados, indent=2, ensure_ascii=False)[:2000])
