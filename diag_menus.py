import glob, os

for arq in ["pc_frontend/analise_patrimonial.html", "pc_frontend/base_legal.html", "pc_frontend/conferencia.html"]:
    print("=" * 70)
    print(f"Arquivo: {arq}")
    print("=" * 70)
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        print(f"  [ERRO] {e}")
        continue
    
    # Procura "Demonstra"
    idx = c.find("Demonstra")
    if idx != -1:
        print("Trecho ao redor de 'Demonstra':")
        print(repr(c[max(0, idx-200):idx+300]))
    else:
        print("  'Demonstra' nao encontrado!")
    print()
