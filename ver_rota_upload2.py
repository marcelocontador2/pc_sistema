c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Mostra o trecho da rota /upload onde as regras de renomeacao estao
idx = c.find('async def upload_arquivo')
if idx == -1:
    print("[ERRO] Funcao upload_arquivo nao encontrada.")
else:
    fim = c.find('@app', idx + 10)
    if fim == -1: fim = len(c)
    
    trecho = c[idx:fim]
    # Mostra as primeiras 100 linhas do trecho
    linhas = trecho.split("\n")
    print("=" * 70)
    print("TRECHO DA ROTA /upload (primeiras 100 linhas)")
    print("=" * 70)
    for i, ln in enumerate(linhas[:100]):
        print(f"{i+1}: {ln}")
