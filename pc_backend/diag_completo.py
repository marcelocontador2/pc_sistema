c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Diagnostico da linha 475
print("=" * 70)
print("LINHA 475 (VARIA... PATRIMONIAL)")
print("=" * 70)
alvo = linhas[474]
print("repr completo:")
print(repr(alvo))
print("\nCodigos Unicode de cada char:")
for ch in alvo:
    print(f"  {repr(ch)}  U+{ord(ch):04X}")

# Diagnostico da linha 580 (PATRIM...NIO)
print("\n" + "=" * 70)
print("LINHA 580 (PATRIM...NIO)")
print("=" * 70)
alvo2 = linhas[579]
print(repr(alvo2))
idx = alvo2.find("PATRIM")
if idx != -1:
    trecho = alvo2[idx:idx+25]
    print("\nCodigos do trecho PATRIM...:")
    for ch in trecho:
        print(f"  {repr(ch)}  U+{ord(ch):04X}")

# Diagnostico da linha 1867
print("\n" + "=" * 70)
print("LINHA 1867 (col_a == VARIA...)")
print("=" * 70)
alvo3 = linhas[1866]
print(repr(alvo3))
