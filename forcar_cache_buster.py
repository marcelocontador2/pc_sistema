c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona um comentário com timestamp no início do arquivo para forçar o cache-buster
import time
timestamp = str(int(time.time()))
if "<!-- CACHE-BUSTER" not in c:
    c = f"<!-- CACHE-BUSTER: {timestamp} -->\n" + c
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Cache-buster adicionado ao index.html!")
else:
    print("[AVISO] Cache-buster já existe.")
