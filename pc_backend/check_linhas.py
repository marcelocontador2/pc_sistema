c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")
# Mostra linhas chave
for alvo in [301, 356, 360, 1044, 1072, 2857]:
    if alvo <= len(linhas):
        print(f"Linha {alvo}: {linhas[alvo-1].strip()[:120]}")
