import re

c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()

print("=" * 70)
print("PROCURANDO 'buscar_valores' NO ARQUIVO")
print("=" * 70)

# Mostra todas as ocorrências de buscar_valores
for i, ln in enumerate(c.split('\n'), 1):
    if 'buscar_valores' in ln:
        print(f"  Linha {i}: {ln.strip()[:150]}")

print("\n" + "=" * 70)
print("PROCURANDO 'Resultado do' NO ARQUIVO")
print("=" * 70)

for i, ln in enumerate(c.split('\n'), 1):
    if 'Resultado do' in ln:
        print(f"  Linha {i}: {ln.strip()[:150]}")
