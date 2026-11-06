c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

print("=" * 70)
print("SCAN PRECISO: caractere + codigo Unicode")
print("=" * 70)

# Foca nas linhas que o scan marcou (exceto 316-320)
alvos = [214, 251, 475, 569, 578, 611, 632, 636, 649, 688, 727, 1461, 1867, 1870, 1873, 1876, 1885, 2716, 4067]

for num in alvos:
    idx = num - 1
    if idx >= len(linhas):
        continue
    ln = linhas[idx]
    # Lista caracteres nao-ASCII
    nao_ascii = [(ch, f"U+{ord(ch):04X}") for ch in ln if ord(ch) > 127]
    if nao_ascii:
        print(f"\nLinha {num}: {repr(ln.strip()[:100])}")
        for ch, codigo in nao_ascii:
            print(f"  {repr(ch)}  {codigo}")
