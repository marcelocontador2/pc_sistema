from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 25700 a 26000) ===")
for i in range(25699, 26000):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
