import requests, json

# Testar a API que a tela de conferencia usa
url = "http://127.0.0.1:9994/api/conferencia/2026-TRIMESTRE-3"
try:
    response = requests.get(url, timeout=10)
    print("Status:", response.status_code)
    print("Resposta:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Erro:", e)
