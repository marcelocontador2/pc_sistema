c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
linhas = c.split('\n')
# Procura onde o título DMPL é montado (perto da linha 517-545)
for i in range(500, 560):
    if i < len(linhas):
        ln = linhas[i]
        if 'Demonstra' in ln or 'Muta' in ln or 'Patrim' in ln or 'titulo' in ln.lower() or 'title' in ln.lower():
            print(f"  Linha {i+1}: {repr(ln.strip()[:200])}")
