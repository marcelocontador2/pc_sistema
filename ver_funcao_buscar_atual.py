c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Localiza a funcao buscar na verificacao do BP
idx = c.find('def buscar(linhas, termos, coluna):')
if idx == -1:
    print("[ERRO] Funcao buscar nao encontrada.")
else:
    # Pega o bloco da funcao (ate o proximo "def" ou 20 linhas)
    fim = c.find('\n        def ', idx + 10)
    if fim == -1:
        fim = idx + 1000
    bloco = c[idx:fim]
    
    print("=" * 70)
    print("FUNCAO buscar ATUAL (contexto da verificacao)")
    print("=" * 70)
    print(bloco)
    
    # Mostra tambem as chamadas da funcao buscar para o BP
    print("\n" + "=" * 70)
    print("CHAMADAS DA FUNCAO buscar PARA O BP")
    print("=" * 70)
    for i, ln in enumerate(c.split("\n"), 1):
        if 'buscar(' in ln and ('PASSIVO' in ln.upper() or 'PATRIM' in ln.upper() or 'TOTAL' in ln.upper() or 'ativo' in ln.lower()):
            print(f"  Linha {i}: {ln.strip()[:150]}")
