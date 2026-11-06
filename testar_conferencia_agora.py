import requests, json

url = "http://127.0.0.1:9994/api/conferencia/2026-TRIMESTRE-3"
try:
    response = requests.get(url, timeout=10)
    print("Status:", response.status_code)
    data = response.json()
    for analise in data.get("analises", []):
        if "Balanço Patrimonial" in analise.get("titulo", ""):
            print(json.dumps(analise, indent=2, ensure_ascii=False))
            break
except Exception as e:
    print("Erro:", e)
