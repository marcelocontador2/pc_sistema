c = open("pc_frontend/liquidez.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) CSS DO .btn-voltar-laranja (linhas 28-40)")
print("=" * 70)
linhas = c.split("\n")
for i in range(27, 40):
    if i < len(linhas):
        print(f"  {i+1}: {linhas[i]}")

print("\n" + "=" * 70)
print("2) BOTOES 'VOLTAR' EM OUTRAS PAGINAS (para comparar)")
print("=" * 70)
import glob, os
for arq in glob.glob("pc_frontend/*.html"):
    try:
        cc = open(arq, encoding="utf-8", errors="ignore").read()
        for i, ln in enumerate(cc.split("\n"), 1):
            if 'voltar' in ln.lower() and ('href=' in ln or 'onclick' in ln):
                print(f"  {os.path.basename(arq)} - Linha {i}: {ln.strip()[:150]}")
                break
    except:
        pass
