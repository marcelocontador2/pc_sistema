import os

arq = "pc_frontend/liquidez.html"
if not os.path.exists(arq):
    print(f"[ERRO] Arquivo {arq} nao encontrado.")
else:
    c = open(arq, encoding="utf-8", errors="ignore").read()
    
    print("=" * 70)
    print("1) BOTOES QUE CONTEM 'VOLTAR'")
    print("=" * 70)
    # Procura tags <a> ou <button> com "voltar" dentro
    for i, ln in enumerate(c.split("\n"), 1):
        if 'voltar' in ln.lower():
            print(f"  Linha {i}: {ln.strip()[:200]}")

    print("\n" + "=" * 70)
    print("2) FUNCOES JAVASCRIPT QUE CONTEM 'voltar'")
    print("=" * 70)
    for i, ln in enumerate(c.split("\n"), 1):
        if 'function' in ln and 'voltar' in ln.lower():
            print(f"  Linha {i}: {ln.strip()[:200]}")
