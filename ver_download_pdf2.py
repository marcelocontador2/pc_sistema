import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO: FUNÇÃO download_pdf (até a próxima rota)")
print("=" * 70)

inicio = c.find('async def download_pdf(')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
else:
    # Pega até a próxima rota @app. ou até o final do arquivo
    prox = c.find('@app.', inicio + 10)
    if prox == -1:
        prox = len(c)
    
    trecho = c[inicio:prox]
    linhas = trecho.split('\n')
    print(f"Total de linhas da função: {len(linhas)}\n")
    for i, ln in enumerate(linhas, 1):
        print(f"{i:>3}: {ln}")
