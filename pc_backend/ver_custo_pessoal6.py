from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 25400 a 25700) ===")
for i in range(25399, 25700):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
