import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_linha1072_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Padroes exatos (confirmados pelo diagnostico)
# 'PATRIM' + Ã + ” + 'NIO' -> 'PATRIM' + Ô + 'NIO'
antigo1 = "PATRIM" + chr(0xC3) + chr(0x201D) + "NIO"
novo1 = "PATRIM" + chr(0xD4) + "NIO"  # Ô

# 'L' + Ã + \x8d + 'QUIDO' -> 'L' + Í + 'QUIDO'
antigo2 = "L" + chr(0xC3) + chr(0x8D) + "QUIDO"
novo2 = "L" + chr(0xCD) + "QUIDO"  # Í

if antigo1 in c:
    c = c.replace(antigo1, novo1)
    print(f"[OK] Substituido: PATRIMÃ”NIO -> PATRIM{chr(0xD4)}NIO")
else:
    print("[AVISO] Padrao 1 nao encontrado.")

if antigo2 in c:
    c = c.replace(antigo2, novo2)
    print(f"[OK] Substituido: LÃ\\x8dQUIDO -> L{chr(0xCD)}QUIDO")
else:
    print("[AVISO] Padrao 2 nao encontrado.")

open(back_path, "w", encoding="utf-8").write(c)

# Valida
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("\n[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_linha1072_{ts}", back_path)
    print("[OK] Backup restaurado.")
