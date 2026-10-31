from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
print("=== api_custo_pessoal (linhas 24571 a 24800) ===")
for i in range(24570, 24800):
    if linhas[i].strip():
        print(f"{i+1:5d}  {linhas[i]}")
