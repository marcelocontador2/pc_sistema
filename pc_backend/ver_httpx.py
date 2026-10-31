from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
# Encontrar o trecho "httpx.AsyncClient" do PDF completo
for i, l in enumerate(linhas):
    if "httpx.AsyncClient" in l and "custo_pessoal" in "\n".join(linhas[i:i+10]):
        print(f"=== httpx.AsyncClient do PDF completo (linha {i+1}) ===")
        for j in range(i, min(i+15, len(linhas))):
            if linhas[j].strip():
                print(f"{j+1:5d}  {linhas[j]}")
        break
