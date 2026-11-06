c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) PROCURANDO 'Passivo + PL' OU 'Passivo +PL' NO MAIN.PY")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if "passivo" in ln.lower() and "pl" in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:150]}")

print("\n" + "=" * 70)
print("2) PROCURANDO 'Ativo Total' OU 'ativo_total' NO MAIN.PY")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if "ativo_total" in ln.lower() or "ativo total" in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:150]}")

print("\n" + "=" * 70)
print("3) PROCURANDO 'Diferença' OU 'diferenca' NO MAIN.PY")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if "diferen" in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:150]}")
