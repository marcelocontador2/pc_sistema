import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== SELECTS ENCONTRADOS NA TELA ===")
selects = re.findall(r'<select[^>]*>', s)
for sel in selects:
    print(f"  {sel}")

print("\n=== INPUTS ENCONTRADOS (QUE PODEM SER O ANO) ===")
inputs = re.findall(r'<input[^>]*>', s)
for inp in inputs:
    if 'ano' in inp.lower() or 'periodo' in inp.lower():
        print(f"  {inp}")
