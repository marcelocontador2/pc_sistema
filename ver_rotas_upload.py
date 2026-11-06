c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("ROTAS DE UPLOAD EXISTENTES")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if '@app.post' in ln and ('upload' in ln.lower() or 'importar' in ln.lower()):
        print(f"Linha {i}: {ln.strip()}")
