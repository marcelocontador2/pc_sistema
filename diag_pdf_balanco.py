import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO: ROTA /download/pdf/BALANCO")
print("=" * 70)

# Encontra a rota
match = re.search(r'@app\.get\("/download/pdf/\{([^}]+)\}"\)\s*\n(?:async\s+)?def\s+(\w+)\([^)]*\):', c)
if match:
    print(f"Rota encontrada: {match.group(0)[:100]}")
    
    inicio = match.end()
    prox = re.search(r'\n@app\.', c[inicio:])
    fim = inicio + prox.start() if prox else len(c)
    corpo = c[inicio:fim].strip()
    
    print(f"\n--- CORPO DA FUNÇÃO ---")
    for i, linha in enumerate(corpo.split('\n')[:50], 1):
        print(f"  {i}: {linha}")
else:
    print("[AVISO] Rota não encontrada no formato padrão.")
    # Tenta procurar por "download/pdf"
    idx = c.find('/download/pdf')
    if idx != -1:
        print(f"Encontrado em: {c[max(0,idx-100):idx+200]}")
