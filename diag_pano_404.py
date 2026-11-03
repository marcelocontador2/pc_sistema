import re

print("=" * 70)
print("DIAGNÓSTICO: ERRO 404 NO PANORAMA")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# 1. Onde está a frase "Erro ao buscar dados do painel"?
print("\n--- ONDE ESTÁ A MENSAGEM DE ERRO ---")
for i, linha in enumerate(c_back.splitlines(), 1):
    if "Erro ao buscar dados do painel" in linha:
        print(f"Linha {i}: {linha.strip()}")

# 2. Como o FastAPI serve a página do Panorama?
print("\n--- COMO O FASTAPI SERVE A TELA DE PANORAMA ---")
rotas = re.findall(r'@app\.get\(["\'](/[^"\']*panorama[^"\']*)["\']\)', c_back)
for r in rotas:
    print(f"Rota: {r}")

# 3. Como a rota gerar_pdf_panorama foi criada no final do arquivo?
print("\n--- CÓDIGO DA ROTA gerar_pdf_panorama NO FINAL DO ARQUIVO ---")
match = re.search(r'(@app\.get\("/gerar_pdf_panorama/\{historico_id\}"\).*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)
if match:
    print(match.group(1).strip()[:1000])
