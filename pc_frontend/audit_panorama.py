import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNCAO carregar/verificar DO PANORAMA ===")
match = re.search(r'function\s+(carregar|verificar|buscarDados|carregarPanorama)\s*\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:2500])
else:
    print("Funcao nao encontrada.")

print("\n=== 2. ROTAS FETCH UTILIZADAS ===")
fetches = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]\)', s)
for f in sorted(set(fetches)):
    print(f"  - {f}")
