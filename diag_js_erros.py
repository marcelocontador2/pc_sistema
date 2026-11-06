import glob, os

print("=" * 70)
print("PROCURANDO A RENDERIZACAO DOS ERROS (1), (2) NOS ARQUIVOS JS")
print("=" * 70)

for arq in glob.glob("pc_frontend/**/*.js", recursive=True):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except:
        continue
    
    if '(1)' in c or 'conferencia' in c.lower() or 'diverg' in c.lower() or 'alerta' in c.lower():
        print(f"\nArquivo: {arq}")
        for i, ln in enumerate(c.split("\n"), 1):
            if 'innerHTML' in ln or 'appendChild' in ln or '<td' in ln or 'erro' in ln.lower() or 'diverg' in ln.lower():
                print(f"  Linha {i}: {ln.strip()[:180]}")
