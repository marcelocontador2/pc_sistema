from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
inicio = 24548
fim = inicio + 1
while fim < len(linhas):
    stripped = linhas[fim].lstrip()
    if stripped.startswith("@app.") or stripped.startswith("def ") or stripped.startswith("class "):
        break
    fim += 1

print(f"Funcao da linha {inicio+1} ate {fim}:")
print()
for i in range(inicio, fim):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
