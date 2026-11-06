c = open("pc_frontend/liquidez.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("BOTOES 'VOLTAR' NO liquidez.html (AGORA)")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'voltar' in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:200]}")
