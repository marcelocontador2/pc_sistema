import re

c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
linhas = c.split('\n')

print("=" * 70)
print("TODAS AS CHAMADAS DE pdf.multi_cell OU pdf.cell QUE ESCREVEM TEXTO")
print("=" * 70)

for i, ln in enumerate(linhas, 1):
    if ('pdf.multi_cell' in ln or 'pdf.cell' in ln):
        # Mostra apenas as que têm texto (não só posicionamento)
        if 'border' in ln or 'align' in ln or '"' in ln or "'" in ln:
            print(f"{i:>4}: {ln.strip()[:150]}")
