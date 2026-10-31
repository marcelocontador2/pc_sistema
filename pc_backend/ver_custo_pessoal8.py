from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 25890 a 26050) ===")
for i in range(25889, 26050):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
