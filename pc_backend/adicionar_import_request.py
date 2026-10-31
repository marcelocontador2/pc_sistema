import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Verifica se o Request já está importado
if "from fastapi import Request" not in c and "from fastapi import" in c:
    # Adiciona o Request ao import existente do FastAPI
    c = re.sub(r'from fastapi import ([^,\n]+)', r'from fastapi import \1, Request', c, count=1)
    print("[OK] Request adicionado ao import do FastAPI.")
elif "from fastapi import Request" not in c:
    # Se não tem nenhum import do FastAPI, adiciona no topo
    c = "from fastapi import FastAPI, Request\n" + c
    print("[OK] Import do FastAPI e Request adicionado no topo.")

# 2. Salva o arquivo
open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
