import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO: FUNÇÃO download_pdf")
print("=" * 70)

inicio = c.find('async def download_pdf(')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
else:
    # Conta chaves para achar o fim
    idx_chave = c.find('{', inicio)
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c):
        if c[i] == '{': nivel += 1
        elif c[i] == '}': nivel -= 1
        i += 1
    
    print(c[inicio:i])
