import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_residual_final_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

G = chr(0x0413)  # Г
mapa = {
    # Principais residuos
    G + chr(0x2021): chr(0xC7),   # Г‡ -> Ç
    G + chr(0x0453): chr(0xC3),   # Гѓ -> Ã (residual que sobrou)
    G + chr(0x0402): chr(0xE3),   # Г‚ -> ã (na linha 611 "nГѓГ‚ВЈo")
    G + chr(0x040E): chr(0xD5),   # ГЎ -> Õ? (na verdade Г• = U+0413+U+040E)
    G + chr(0x040A): chr(0xCD),   # ГЊ -> Í (linha 578 "LГЊQUIDO")
    G + chr(0x00A7): chr(0xE7),   # Г§ -> ç
    G + chr(0x00A3): chr(0xE3),   # ГЈ -> ã
    G + chr(0x00AD): chr(0xED),   # Г -> í
    G + chr(0x201C): chr(0xD4),   # Г” -> Ô (linha 469)
    G + chr(0x201D): chr(0xD4),   # Г” -> Ô variante
    G + chr(0x2039): chr(0xCA),   # ГЉ -> Ê
    G + chr(0x0405): chr(0xCA),   # Г… -> Ê (outra variante)
    G + chr(0x0401): chr(0xD5),   # ГЃ -> Õ? 
    # Casos especiais (1 char)
    G + chr(0x0490) + chr(0x2019): chr(0xC3),  # Ж’ -> Ã
}

alteradas = 0
for i in range(len(linhas)):
    if 315 <= i <= 319:
        continue
    original = linhas[i]
    nova = original
    for _ in range(2):
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

print(f"\n[OK] {alteradas} linhas corrigidas.")

try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"main.py.bak_fix_residual_final_{ts}", "main.py")
    print("[OK] Backup restaurado.")
