import re
import urllib.request
import json

caminho = "pc_frontend/integridade.html"
with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

print("=" * 70)
print("1. IDs REAIS NO HTML")
print("=" * 70)
ids = re.findall(r'id="([^"]+)"', html)
for i in sorted(set(ids)):
    print(f"   - {i}")

print("\n" + "=" * 70)
print("2. ONCLICKS DOS BOTÕES")
print("=" * 70)
onclicks = re.findall(r'onclick="([^"]+)"', html)
for o in onclicks:
    print(f"   - {o}")

print("\n" + "=" * 70)
print("3. FUNÇÕES JAVASCRIPT DEFINIDAS NO HTML")
print("=" * 70)
funcoes = re.findall(r'(?:async\s+)?function\s+(\w+)\s*\(', html)
for f in funcoes:
    print(f"   - {f}")

print("\n" + "=" * 70)
print("4. PRIMEIRAS LINHAS DO <script> ATUAL")
print("=" * 70)
idx_script = html.find("<script>")
if idx_script != -1:
    print(html[idx_script:idx_script+1500])
else:
    print("   ❌ <script> não encontrado")

print("\n" + "=" * 70)
print("5. TESTANDO AS APIs DO BACKEND")
print("=" * 70)
apis = [
    ("GET", "http://127.0.0.1:9994/historico_integridade_matriz"),
    ("GET", "http://127.0.0.1:9994/api/integridade_matriz/2026-TRIMESTRE-3"),
]
for metodo, url in apis:
    print(f"\n   📡 {metodo} {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        if isinstance(data, list):
            print(f"      ✅ Status 200 | Lista com {len(data)} itens")
            if data:
                print(f"      Primeiro item: {data[0]}")
        elif isinstance(data, dict):
            if data.get("erro"):
                print(f"      ❌ Erro: {data.get('mensagem')}")
            else:
                print(f"      ✅ Status 200 | Chaves: {list(data.keys())}")
                if 'matriz' in data:
                    print(f"      Linhas na matriz: {len(data['matriz'])}")
        else:
            print(f"      ✅ Status 200 | Tipo: {type(data)}")
    except Exception as e:
        print(f"      ❌ Erro: {e}")
