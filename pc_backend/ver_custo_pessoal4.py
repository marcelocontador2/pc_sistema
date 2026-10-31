from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 25000 a 25200) ===")
for i in range(24999, 25200):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
