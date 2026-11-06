import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_cirurgico_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

mapa = {
    chr(0xC3)+chr(0xA7): chr(0xE7),
    chr(0xC3)+chr(0xA3): chr(0xE3),
    chr(0xC3)+chr(0xA1): chr(0xE1),
    chr(0xC3)+chr(0xA9): chr(0xE9),
    chr(0xC3)+chr(0xAD): chr(0xED),
    chr(0xC3)+chr(0xB3): chr(0xF3),
    chr(0xC3)+chr(0xBA): chr(0xFA),
    chr(0xC3)+chr(0xA2): chr(0xE2),
    chr(0xC3)+chr(0xAA): chr(0xEA),
    chr(0xC3)+chr(0xB4): chr(0xF4),
    chr(0xC3)+chr(0x87): chr(0xC7),
    chr(0xC3)+chr(0x95): chr(0xD5),
    chr(0xC3)+chr(0xB5): chr(0xF5),
    chr(0xC3)+chr(0x81): chr(0xC1),
    chr(0xC3)+chr(0x8D): chr(0xCD),
    chr(0xC3)+chr(0x93): chr(0xD3),
    chr(0xC3)+chr(0x94): chr(0xD4),
    chr(0xC3)+chr(0x8A): chr(0xCA),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA7): chr(0xE7),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA3): chr(0xE3),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA1): chr(0xE1),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA9): chr(0xE9),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xAD): chr(0xED),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xB3): chr(0xF3),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xBA): chr(0xFA),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x87): chr(0xC7),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x95): chr(0xD5),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x8D): chr(0xCD),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x93): chr(0xD3),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x94): chr(0xD4),
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x8A): chr(0xCA),
}

alteradas = 0
for i in range(len(linhas)):
    if 315 <= i <= 319:
        continue
    original = linhas[i]
    nova = original
    for antigo, novo in mapa.items():
        if antigo in nova:
            nova = nova.replace(antigo, novo)
    if nova != original:
        linhas[i] = nova
        alteradas += 1
        if alteradas <= 20:
            print(f"[{i+1}] {repr(original.strip()[:70])}")
            print(f"     -> {repr(nova.strip()[:70])}")

c_novo = "\n".join(linhas)
open("main.py", "w", encoding="utf-8").write(c_novo)

print(f"\n[OK] {alteradas} linhas corrigidas (fora das 316-320).")

try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"main.py.bak_fix_cirurgico_{ts}", "main.py")
    print("[OK] Backup restaurado.")
