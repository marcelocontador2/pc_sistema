import os, glob

print("=" * 70)
print("1) ARQUIVO DO ROTEADOR BF (que contem a API de calculo)")
print("=" * 70)
caminhos = ["pc_backend/app/routers/balanco_financeiro.py", "pc_backend/routers/balanco_financeiro.py"]
achou_router = False
for caminho in caminhos:
    if os.path.exists(caminho):
        print(f"[OK] Encontrado: {caminho}")
        achou_router = True
        break
if not achou_router:
    # Procura em qualquer lugar
    for f in glob.glob("pc_backend/**/balanco_financeiro.py", recursive=True):
        print(f"[OK] Encontrado em: {f}")
        achou_router = True
        break
if not achou_router:
    print("[AVISO] Arquivo do roteador BF nao encontrado. Listando pastas 'routers':")
    for f in glob.glob("pc_backend/**/routers", recursive=True):
        print(f"  {f}")

print("\n" + "=" * 70)
print("2) FUNCOES NO HTML DE ANALISE FINANCEIRA BF (estrutura da tela)")
print("=" * 70)
try:
    c = open("pc_frontend/analise_financeira_bf.html", encoding="utf-8", errors="ignore").read()
    # Lista funcoes JS
    import re
    for m in re.finditer(r'function\s+(\w+)', c):
        print(f"  function {m.group(1)}")
    print("\n  --- IDs de elementos ---")
    for m in re.finditer(r'id="([^"]+)"', c):
        print(f"  id=\"{m.group(1)}\"")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("3) ROTA /analise_financeira_bf NO MAIN.PY (que serve o HTML)")
print("=" * 70)
c = open("pc_backend/main.py", encoding="utf-8-sig").read()
idx = c.find('@app.get("/analise_financeira_bf")')
if idx != -1:
    fim = c.find('@app', idx + 10)
    if fim == -1: fim = idx + 500
    print(c[idx:fim])
