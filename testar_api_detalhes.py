import urllib.request, json
url = "http://127.0.0.1:9994/api/comparativo_despesas_v2/2026-TRIMESTRE-3"
with urllib.request.urlopen(url) as r:
    data = json.loads(r.read().decode())
print("Chaves do JSON:", list(data.keys()))
print("detalhes na resposta:", len(data.get("detalhes", [])))
if data.get("detalhes"):
    for d in data["detalhes"][:3]:
        print(" ", d)
