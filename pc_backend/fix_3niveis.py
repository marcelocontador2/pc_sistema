import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_3niveis_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

G = chr(0x0413)  # letra cirilica GHE, base do mojibake de 3 niveis
mapa = {
    # Padroes de 3 niveis (Г + chars Latin-1/CP1252)
    G + chr(0x0453) + chr(0x0402) + chr(0x0407): chr(0xC7),  # ГѓвЂЎ -> Ç
    G + chr(0x0453) + chr(0x0402) + chr(0x040E): chr(0xD5),  # ГѓвЂў -> Õ
    G + chr(0x0453) + chr(0x0490) + chr(0x2019): chr(0xC3),  # ГѓЖ’ -> Ã
    G + chr(0x0453) + chr(0x0405) + " ": chr(0xCA),  # ГѓЕ -> Ê
    G + chr(0x0453) + chr(0x0402) + chr(0x00A7): chr(0xE7),  # ГѓВ§ -> ç
    G + chr(0x0453) + chr(0x0402) + chr(0x0408): chr(0xE3),  # ГѓВЈ -> ã (variante)
    G + chr(0x0453) + chr(0x0402) + chr(0x00A1): chr(0xE1),  # ГѓВЎ -> á
    G + chr(0x0453) + chr(0x0402) + chr(0x00A9): chr(0xE9),  # ГѓВ© -> é
    G + chr(0x0453) + chr(0x0402) + chr(0x00AD): chr(0xED),  # ГѓВ -> í
    G + chr(0x0453) + chr(0x0402) + chr(0x00B3): chr(0xF3),  # ГѓВі -> ó
    G + chr(0x0453) + chr(0x0402) + chr(0x0404): chr(0xEA),  # ГѓВЄ -> ê
    G + chr(0x0453) + chr(0x0402) + chr(0x0491): chr(0xF4),  # ГѓВґ -> ô
    G + chr(0x0453) + chr(0x0402) + chr(0x040A): chr(0xFA),  # ГѓВє -> ú
    G + chr(0x0453) + chr(0x0402) + chr(0x0403): chr(0xE2),  # ГѓВў -> â
    # Padroes de 2 niveis remanescentes
    G + chr(0x0453) + chr(0x201C): chr(0xD4),  # Г” -> Ô
    G + chr(0x040A): chr(0xCD),  # ГЊ -> Í
    # Padroes de 1 nivel (linha 4067)
    G + chr(0x00A7): chr(0xE7),  # Г§ -> ç
    G + chr(0x00A3): chr(0xE3),  # ГЈ -> ã
    G + chr(0x00AD): chr(0xED),  # Г -> í
    # Caso especial: ГѓЖ’Гўв‚¬\x9dNIO
    G + chr(0x0453) + chr(0x0490) + chr(0x2019) + G + chr(0x00A2) + chr(0x0432) + chr(0x201A) + chr(0x00AC): chr(0xD4),  # PATRIMÔNIO
}

alteradas = 0
for i in range(len(linhas)):
    # PULA as linhas 316-320 (codigo de fix em runtime)
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
        if alteradas <= 30:
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
    shutil.copy2(f"main.py.bak_fix_3niveis_{ts}", "main.py")
    print("[OK] Backup restaurado.")
