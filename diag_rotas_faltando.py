c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) ROTAS QUE CONTEM 'custo' OU 'pessoal'")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if '@app.get' in ln and ('custo' in ln.lower() or 'pessoal' in ln.lower()):
        print(f"  Linha {i}: {ln.strip()}")

print("\n" + "=" * 70)
print("2) ROTAS QUE CONTEM 'centro' OU 'custos'")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if '@app.get' in ln and ('centro' in ln.lower() or 'custos' in ln.lower()):
        print(f"  Linha {i}: {ln.strip()}")

print("\n" + "=" * 70)
print("3) ROTAS QUE CONTEM 'comparativo'")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if '@app.get' in ln and 'comparativo' in ln.lower():
        print(f"  Linha {i}: {ln.strip()}")
