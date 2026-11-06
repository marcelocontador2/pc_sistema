c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Procura a rota /liquidez
for i, ln in enumerate(c.split("\n"), 1):
    if '@app.get("/liquidez")' in ln:
        # Mostra a rota e as linhas seguintes
        linhas = c.split("\n")
        print(f"Linha {i}: {ln.strip()}")
        for j in range(i, min(i+10, len(linhas))):
            print(f"  {j+1}: {linhas[j]}")
        break
