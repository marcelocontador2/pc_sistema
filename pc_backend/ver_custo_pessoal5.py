from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 25200 a 25400) ===")
for i in range(25199, 25400):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
