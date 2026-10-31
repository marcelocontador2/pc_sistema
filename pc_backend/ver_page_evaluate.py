from pathlib import Path

linhas = Path("main.py").read_text(encoding="utf-8").splitlines()
# Encontrar o "page.evaluate" do PDF completo
for i, l in enumerate(linhas):
    if "page.evaluate" in l and "pdf-rcl-total" in "\n".join(linhas[i:i+20]):
        print(f"=== page.evaluate do PDF completo (linha {i+1}) ===")
        for j in range(i, min(i+30, len(linhas))):
            if linhas[j].strip():
                print(f"{j+1:5d}  {linhas[j]}")
        break
