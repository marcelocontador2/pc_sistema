import re

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Padroes que indicam mojibake (texto UTF-8 lido como Latin-1)
padroes = [
    "Ã",      # prefixo de quase todo mojibake
    "\xad",   # soft hyphen (invisivel)
    "\x8d", "\x9d", "\x9f", "\x83", "\x82",  # caracteres de controle Latin-1
]

print("=" * 70)
print("VARREDURA DE MOJIBAKE NO main.py")
print("=" * 70)

total = 0
for i, ln in enumerate(linhas, 1):
    # Ignora linhas de comentario e encoding
    if "encoding" in ln.lower() or "coding:" in ln.lower():
        continue
    for p in padroes:
        if p in ln:
            # Trunca linhas muito longas
            texto = ln.strip()
            if len(texto) > 180:
                texto = texto[:180] + "..."
            print(f"  Linha {i}: {repr(texto)}")
            total += 1
            break  # nao duplica se tiver mais de um padrao na mesma linha

print(f"\nTotal de linhas com mojibake: {total}")
