from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 24790 a 25000) ===")
for i in range(24789, 25000):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
