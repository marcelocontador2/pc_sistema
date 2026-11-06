import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_residual_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Substituicoes manuais para padroes residuais de mojibake triplo
# Usando chr() para nao corromper no terminal
subs = {
    "PATRIM" + chr(195) + chr(226) + chr(8364) + chr(157) + "NIO": "PATRIM" + chr(212) + "NIO",  # Ã¢â€NIO -> ÔNIO
    "PATRIM" + chr(195) + chr(226) + chr(8220) + "NIO": "PATRIM" + chr(212) + "NIO",
    "L" + chr(195) + "QUIDO": "L" + chr(205) + "QUIDO",  # LÃQUIDO -> LÍQUIDO
    chr(195) + chr(162) + chr(8364) + chr(157) + "NIO": chr(212) + "NIO",
}

alteradas = 0
for antigo, novo in subs.items():
    if antigo in c:
        c = c.replace(antigo, novo)
        alteradas += 1
        print(f"[OK] Substituido: {repr(antigo)} -> {repr(novo)}")

# Fallback: substituicao direta dos dois casos conhecidos
c = c.replace('"TOTAL DO PATRIM' + chr(195) + chr(226) + chr(8364) + chr(157) + 'NIO L' + chr(195) + 'QUIDO"',
              '"TOTAL DO PATRIM' + chr(212) + 'NIO L' + chr(205) + 'QUIDO"')
c = c.replace('"TOTAL DO PATRIM' + chr(195) + chr(226) + chr(8220) + 'NIO L' + chr(195) + 'QUIDO"',
              '"TOTAL DO PATRIM' + chr(212) + 'NIO L' + chr(205) + 'QUIDO"')

open(back_path, "w", encoding="utf-8").write(c)

# Valida
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("\n[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_residual_{ts}", back_path)
    print("[OK] Backup restaurado.")
