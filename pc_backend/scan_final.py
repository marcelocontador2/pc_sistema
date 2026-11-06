c = open("main.py", encoding="utf-8-sig").read()
residuos = []
for i, ln in enumerate(c.split("\n"), 1):
    for ch in ln:
        code = ord(ch)
        if 0x80 <= code <= 0x9F or code == 0xAD or ch == "Ã":
            residuos.append((i, ln.strip()[:120]))
            break

if residuos:
    print(f"[AVISO] {len(residuos)} linha(s) com residuo de mojibake:")
    for i, txt in residuos:
        print(f"  Linha {i}: {repr(txt)}")
else:
    print("[OK] Nenhum residuo de mojibake encontrado!")
