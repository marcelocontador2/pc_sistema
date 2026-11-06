c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Mostra o codigo da rota /upload (da linha 755 ate a proxima @app)
inicio = 754  # indice da linha 755
fim = inicio
for i in range(inicio, len(linhas)):
    if i > inicio and '@app' in linhas[i]:
        fim = i
        break

print("=" * 70)
print("CODIGO DA ROTA /upload")
print("=" * 70)
for i in range(inicio, min(fim, inicio + 100)):
    print(f"{i+1}: {linhas[i]}")
