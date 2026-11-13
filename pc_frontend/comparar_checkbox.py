import re

# 1. Ver como o DMPL monta o checkbox (que funciona)
with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    dmpl = f.read()

print("=== CHECKBOX NO DMPL (QUE FUNCIONA) ===")
match = re.search(r'<input[^>]*class="[^"]*check-hist[^"]*"[^>]*>', dmpl)
if match:
    print(match.group(0))
else:
    print("Nao encontrado no DMPL.")

# 2. Ver como o Panorama monta o checkbox (que nao funciona)
with open("panorama.html", "r", encoding="utf-8") as f:
    pano = f.read()

print("\n=== CHECKBOX NO PANORAMA (QUEBRADO) ===")
match = re.search(r'<input[^>]*class="[^"]*check-historico[^"]*"[^>]*>', pano)
if match:
    print(match.group(0))
else:
    print("Nao encontrado no Panorama (pode estar sendo gerado via JS).")

# 3. Mostra como o JS do Panorama gera o checkbox
print("\n=== JS DO PANORAMA QUE GERA O CHECKBOX ===")
match = re.search(r'html \+= `<li>.*?</li>`;', pano, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("Nao encontrado.")
