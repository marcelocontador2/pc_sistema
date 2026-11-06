import requests, json, re

print("=== 1) TESTANDO A API DIRETAMENTE ===")
url = "http://127.0.0.1:9994/api/panorama/2026-TRIMESTRE-3"
try:
    r = requests.get(url, timeout=10)
    print("Status:", r.status_code)
    print("Resposta JSON:")
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Erro ao conectar na API:", e)

print("\n=== 2) EXTRAINDO O RESTO DAS FUNCOES JS ===")
arquivo = r"pc_frontend\panorama.html"
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Pega o bloco da funcao carregarPanorama inteira
idx = html.find("async function carregarPanorama")
end = html.find("async function salvarPanorama")
if idx != -1 and end != -1:
    bloco = html[idx:end]
    print("--- Funcao carregarPanorama ---")
    print(bloco[:2500]) # Exibe os primeiros 2500 caracteres para nao lotar
else:
    print("[ERRO] Nao foi possivel isolar a funcao carregarPanorama.")

# Pega a funcao carregarHistorico
idx_hist = html.find("function carregarHistorico")
end_hist = html.find("function exibirSelecionado")
if idx_hist != -1 and end_hist != -1:
    bloco_hist = html[idx_hist:end_hist]
    print("\n--- Funcao carregarHistorico ---")
    print(bloco_hist[:1500])
