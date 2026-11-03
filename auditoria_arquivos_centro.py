import os

print("=" * 70)
print("ARQUIVOS DE RELATÓRIO DE CENTRO DE CUSTOS NA PASTA")
print("=" * 70)

arquivos = [f for f in os.listdir("pc_frontend") if "centro" in f.lower() and f.endswith(".html")]
for f in arquivos:
    caminho = os.path.join("pc_frontend", f)
    tamanho = os.path.getsize(caminho)
    print(f"\n📄 {f} ({tamanho} bytes)")

    # Mostra o título e as primeiras linhas
    try:
        c = open(caminho, encoding="utf-8").read()
        print(f"   Título: {c[:200]}")
        # Conta elementos-chave
        print(f"   Cards (.card/.kpi-card): {c.count('card')}")
        print(f"   Gráficos (canvas): {c.count('<canvas')}")
        print(f"   Tabelas (<table>): {c.count('<table')}")
    except Exception as e:
        print(f"   Erro ao ler: {e}")

print("\n" + "=" * 70)
print("COMO O BACKEND ESTÁ CHAMANDO O PLAYWRIGHT (main.py)")
print("=" * 70)
c_back = open("pc_backend/main.py", encoding="utf-8-sig").read()

import re
# Procura a rota de PDF do centro de custos
matches = re.findall(r'url = f"http://127\.0\.0\.1:9994/([^"+\?]+)', c_back)
for m in matches:
    if "centro" in m.lower() or "relatorio" in m.lower():
        print(f"  Playwright abre: /{m}")

# Também procura dentro do corpo da rota /gerar_pdf_centro_custos
match = re.search(r'def gerar_pdf_centro_custos.*?(?=\n@app\.|\Z)', c_back, re.DOTALL)
if match:
    print("\n--- Corpo da rota gerar_pdf_centro_custos ---")
    # Acha a URL dentro dela
    urls = re.findall(r'f"(http[^"]+)"', match.group(0))
    for u in urls:
        print(f"  URL: {u}")
