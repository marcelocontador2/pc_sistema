import requests, json

# Pega o último ID salvo no histórico
try:
    res_hist = requests.get("http://127.0.0.1:9994/historico_panorama")
    ultimo_id = res_hist.json()[0]['id']
    print(f"Testando o ID mais recente do historico: {ultimo_id}\n")
    
    # Puxa os dados desse ID
    res = requests.get(f"http://127.0.0.1:9994/historico_panorama/{ultimo_id}")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Erro ao consultar API:", e)
