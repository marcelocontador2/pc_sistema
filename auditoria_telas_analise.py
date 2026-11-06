import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Lista as rotas de telas de análise (HTML)
rotas_tela = re.findall(r'@app\.get\("(/analise[^"]*)"\)', codigo)
print("=" * 70)
print("ROTAS DE TELA (HTML) DE ANÁLISE")
print("=" * 70)
for r in sorted(set(rotas_tela)):
    print(f"  {r}")

# 2. Lista os arquivos HTML no frontend
import os
print("\n" + "=" * 70)
print("ARQUIVOS HTML NO FRONTEND")
print("=" * 70)
for f in sorted(os.listdir("pc_frontend")):
    if f.startswith("analise_") and f.endswith(".html"):
        print(f"  {f}")

# 3. Para cada rota, verifica se retorna FileResponse ou HTMLResponse
print("\n" + "=" * 70)
print("COMO CADA TELA É SERVIDA")
print("=" * 70)
for rota in sorted(set(rotas_tela)):
    idx = codigo.find(f'@app.get("{rota}"')
    if idx != -1:
        fim = codigo.find("\n@app.", idx + 10)
        bloco = codigo[idx:fim if fim != -1 else idx+500]
        if "FileResponse" in bloco:
            arq = re.search(r'"([^"]+\.html)"', bloco)
            nome = arq.group(1) if arq else "?"
            print(f"  {rota} → FileResponse({nome})")
        elif "HTMLResponse" in bloco:
            print(f"  {rota} → HTMLResponse (inline)")
        else:
            print(f"  {rota} → outro")
