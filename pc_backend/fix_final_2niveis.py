import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_final_2niveis_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Padroes reais (confirmados pelo diagnostico)
# C3 = Ã (U+00C3), 2021 = ‡ (U+2021), 0192 = ƒ (U+0192)
A = chr(0xC3)  # Ã
mapa = {
    # 2 niveis -> 1 acento
    A + chr(0x2021): chr(0xC7),  # Ã‡ -> Ç
    A + chr(0x0192): A,          # Ãƒ -> Ã (residual)
    A + chr(0x2022): chr(0xD5),  # Ã• -> Õ (bullet U+2022)
    A + chr(0x2039): chr(0xCA),  # ÃŠ -> Ê (U+2039)
    A + chr(0x201C): chr(0xD4),  # Ã” -> Ô (U+201C)
    A + chr(0x201D): chr(0xD4),  # Ã” -> Ô (U+201D, variante)
    A + chr(0x0160): chr(0xC3),  # ÃŠ -> Ã (residual)
    A + chr(0x2013): chr(0xD5),  # Ã• -> Õ (en-dash)
    # 1 nivel (casos que sobraram)
    A + chr(0xA7): chr(0xE7),  # Ã§ -> ç
    A + chr(0xA3): chr(0xE3),  # Ã£ -> ã
    A + chr(0xA1): chr(0xE1),  # Ã¡ -> á
    A + chr(0xA9): chr(0xE9),  # Ã© -> é
    A + chr(0xAD): chr(0xED),  # Ã -> í
    A + chr(0xB3): chr(0xF3),  # Ã³ -> ó
    A + chr(0xBA): chr(0xFA),  # Ãº -> ú
    A + chr(0xA2): chr(0xE2),  # Ã¢ -> â
    A + chr(0xAA): chr(0xEA),  # Ãª -> ê
    A + chr(0xB4): chr(0xF4),  # Ã´ -> ô
    A + chr(0x87): chr(0xC7),  # Ã‡ -> Ç
    A + chr(0x95): chr(0xD5),  # Ã• -> Õ
    A + chr(0x81): chr(0xC1),  # Ã -> Á
    A + chr(0x8D): chr(0xCD),  # Ã\x8d -> Í
    A + chr(0x93): chr(0xD3),  # Ã“ -> Ó
    A + chr(0x94): chr(0xD4),  # Ã” -> Ô
    A + chr(0x8A): chr(0xCA),  # ÃŠ -> Ê
}

alteradas = 0
for i in range(len(linhas)):
    # PULA as linhas 316-320 (codigo de fix em runtime)
    if 315 <= i <= 319:
        continue
    original = linhas[i]
    nova = original
    # Aplica 2 passadas para pegar mojibake de 2 niveis
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

print(f"\n[OK] {alteradas} linhas corrigidas (fora das 316-320).")

try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"main.py.bak_fix_final_2niveis_{ts}", "main.py")
    print("[OK] Backup restaurado.")
