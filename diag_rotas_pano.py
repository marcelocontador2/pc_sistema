import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("TODAS AS ROTAS DE PDF DO PANORAMA NO MAIN.PY")
print("=" * 70)

# Procura todas as rotas que tenham "gerar_pdf_panorama"
matches = re.finditer(r'(@app\.get\("/gerar_pdf_panorama/[^"]+"\)\s*\n(?:async\s+)?def\s+([a-zA-Z0-9_]+)\([^)]*\):)', c, re.IGNORECASE)

encontrou = False
for m in matches:
    print("\n" + "-"*50)
    print(m.group(1))
    encontrou = True

if not encontrou:
    print("[AVISO] Nenhuma rota de PDF do Panorama encontrada!")
