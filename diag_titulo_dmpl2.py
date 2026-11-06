c = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
linhas = c.split('\n')

print("=" * 70)
print("1) LINHAS COM 'Demonstra' / 'Muta' / 'Patrim' (case-insensitive)")
print("=" * 70)
for i, ln in enumerate(linhas, 1):
    low = ln.lower()
    if 'demonstra' in low or 'muta' in low or 'patrim' in low:
        print(f"  Linha {i}: {repr(ln.strip()[:200])}")

print("\n" + "=" * 70)
print("2) LINHAS COM 'titulo' (case-insensitive)")
print("=" * 70)
for i, ln in enumerate(linhas, 1):
    if 'titulo' in ln.lower():
        print(f"  Linha {i}: {repr(ln.strip()[:200])}")

print("\n" + "=" * 70)
print("3) LINHAS COM 'fpdf' / 'FPDF' / 'pdf.set_font' ANTES DA LINHA 500")
print("=" * 70)
for i, ln in enumerate(linhas[:500], 1):
    if 'fpdf' in ln.lower() or 'pdf =' in ln or 'def gerar' in ln.lower():
        print(f"  Linha {i}: {repr(ln.strip()[:200])}")
