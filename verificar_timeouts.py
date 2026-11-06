import re

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    print(f"\n{'='*70}")
    print(f"VERIFICANDO: {arq}")
    print(f"{'='*70}")
    
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        print(f"  [ERRO] {e}")
        continue
    
    # Conta ocorrencias de setTimeout
    timeouts = c.count("setTimeout")
    print(f"  setTimeout encontrados: {timeouts}")
    
    # Conta ocorrencias de submenuAnalises
    submenu = c.count("submenuAnalises")
    print(f"  submenuAnalises encontrados: {submenu}")
    
    # Mostra os trechos de script que contem setTimeout
    for i, ln in enumerate(c.split("\n"), 1):
        if 'setTimeout' in ln:
            print(f"  Linha {i}: {ln.strip()[:120]}")
