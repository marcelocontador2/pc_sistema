import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Procura a função api_panorama
idx = codigo.find("async def api_panorama(")
if idx == -1:
    idx = codigo.find("def api_panorama(")

if idx != -1:
    # Pega até a próxima @app ou def
    fim = codigo.find("\n@app.", idx)
    if fim == -1:
        fim = codigo.find("\ndef ", idx)
    if fim == -1:
        fim = idx + 3000
    
    print("=== CÓDIGO ATUAL DA API DO PANORAMA ===")
    print(codigo[idx:fim])
else:
    print("[ERRO] Funcao api_panorama nao encontrada no main.py.")
