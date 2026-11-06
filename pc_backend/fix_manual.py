import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_manual_{ts}")

c = open("main.py", encoding="utf-8-sig").read()

# Mapa manual de mojibake residual (2 niveis)
# Ã = U+00C3, Â = U+00C2, £ = U+00A3, § = U+00A7, ¡ = U+00A1
A = chr(0xC3)  # Ã
Ac = chr(0xC2)  # Â
mapa = {
    # "nÃÂ£o" -> "não"
    A + Ac + chr(0xA3) + "o": chr(0xE3) + "o",  # ÃÂ£o -> ão
    # "PerÃÂodo" -> "Período"
    A + Ac + "odo": chr(0xED) + "odo",  # ÃÂodo -> íodo
    # "CabeÃÂ§alho" -> "Cabeçalho"
    A + Ac + chr(0xA7) + "alho": chr(0xE7) + "alho",  # ÃÂ§alho -> çalho
    # "PATRIMÃâ€\x9dNIO" -> "PATRIMÔNIO"
    A + chr(0xE2) + chr(0x80) + chr(0x9D) + "NIO": chr(0xD4) + "NIO",  # Ãâ€\x9dNIO -> ÔNIO
    # "ESPECIFICAÃâ€¡ÃÆ'O" -> "ESPECIFICAÇÃO"
    A + chr(0xE2) + chr(0x80) + chr(0xA1) + A + chr(0xC6) + chr(0x92) + "O": chr(0xC7) + chr(0xC3) + "O",
    # "TRANSFERÃNCIAS" -> "TRANSFERÊNCIAS"
    A + "NCIAS": chr(0xCA) + "NCIAS",  # ÃNCIAS -> ÊNCIAS
    # "DELEGAÇÕES" ja correto, nao mexer
}

alteradas = 0
for antigo, novo in mapa.items():
    if antigo in c:
        n_vezes = c.count(antigo)
        c = c.replace(antigo, novo)
        alteradas += n_vezes
        print(f"[OK] {n_vezes}x: {repr(antigo)} -> {repr(novo)}")

open("main.py", "w", encoding="utf-8").write(c)
print(f"\n[OK] {alteradas} substituicoes.")

try:
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"main.py.bak_fix_manual_{ts}", "main.py")
    print("[OK] Backup restaurado.")
