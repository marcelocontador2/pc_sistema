import re, requests

print("=== 1) TESTANDO A ROTA DO HISTORICO ===")
try:
    r = requests.get("http://127.0.0.1:9994/historico_panorama", timeout=10)
    print("Status:", r.status_code)
    print("Resposta:", r.text[:500])
except Exception as e:
    print("Erro:", e)

print("\n=== 2) FUNCAO APLICAR VALORES (JS) ===")
arquivo = r"pc_frontend\panorama.html"
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

idx = html.find("function aplicarValores")
end = html.find("async function carregarPanorama")
if idx != -1 and end != -1:
    print(html[idx:end].strip())
else:
    print("[ERRO] Funcao aplicarValores nao encontrada!")

print("\n=== 3) IDS DOS ELEMENTOS NO HTML ===")
# Procura por elementos com id que pareçam ser os cards
ids = re.findall(r'id=["\']([^"\']+)["\']', html)
print("IDs encontrados no HTML:")
for i in sorted(set(ids)):
    # Mostra apenas os que tem a ver com os dados do panorama
    if any(k in i.lower() for k in ['card', 'ativo', 'passivo', 'caixa', 'receita', 'despesa', 'superavit', 'deficit', 'lista', 'historico', 'btn']):
        print(f"  - {i}")
