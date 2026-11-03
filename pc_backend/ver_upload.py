linhas = open('main.py', encoding='utf-8-sig').read().splitlines()
idxs = [i for i, ln in enumerate(linhas) if '@app.post("/upload")' in ln]
print(f"Ocorrencias: {[i+1 for i in idxs]}\n")
if idxs:
    ini = idxs[0]
    for j in range(ini, min(ini + 70, len(linhas))):
        print(f"{j+1:>5}: {linhas[j]}")
