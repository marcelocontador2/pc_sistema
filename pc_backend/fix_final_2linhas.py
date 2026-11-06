import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_final_2linhas_{ts}")

c = open("main.py", encoding="utf-8-sig").read()

# Padroes exatos (confirmados pelo scan_preciso)
A = chr(0xC3)  # Ã
E = chr(0xE2)  # â
E2 = chr(0x20AC)  # €
SH = chr(0x9D)  # \x9d
I = chr(0xA1)  # ¡
AE = chr(0xC6)  # Æ
AP = chr(0x2019)  # '

# Linha 649: PATRIMÃâ€\x9dNIO -> PATRIMÔNIO
antigo1 = "PATRIM" + A + E + E2 + SH + "NIO"
novo1 = "PATRIM" + chr(0xD4) + "NIO"
if antigo1 in c:
    c = c.replace(antigo1, novo1)
    print(f"[OK] Linha 649: PATRIM...NIO -> PATRIM{chr(0xD4)}NIO")

# Linha 727: ESPECIFICAÃâ€¡ÃÆ'O -> ESPECIFICAÇÃO
antigo2 = "ESPECIFICA" + A + E + E2 + I + A + AE + AP + "O"
novo2 = "ESPECIFICA" + chr(0xC7) + chr(0xC3) + "O"
if antigo2 in c:
    c = c.replace(antigo2, novo2)
    print(f"[OK] Linha 727: ESPECIFICA... -> ESPECIFICA{chr(0xC7)}{chr(0xC3)}O")
else:
    print("[AVISO] Padrao da linha 727 nao encontrado. Tentando variante...")
    # Tenta variante sem o apóstrofo final
    antigo2b = "ESPECIFICA" + A + E + E2 + I + A + AE + "O"
    if antigo2b in c:
        c = c.replace(antigo2b, novo2)
        print(f"[OK] Linha 727 (variante): -> ESPECIFICA{chr(0xC7)}{chr(0xC3)}O")

open("main.py", "w", encoding="utf-8").write(c)

try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"main.py.bak_fix_final_2linhas_{ts}", "main.py")
    print("[OK] Backup restaurado.")
