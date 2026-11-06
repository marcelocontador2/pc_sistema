import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_2niveis_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Mapa de substituicoes: mojibake (1 nivel) -> char correto
# Usando chr() para evitar corrupcao no terminal
mapa = {
    # 1 nivel
    chr(0xC3)+chr(0xA7): chr(0xE7),  # Ã§ -> ç
    chr(0xC3)+chr(0xA3): chr(0xE3),  # Ã£ -> ã
    chr(0xC3)+chr(0xA1): chr(0xE1),  # Ã¡ -> á
    chr(0xC3)+chr(0xA9): chr(0xE9),  # Ã© -> é
    chr(0xC3)+chr(0xAD): chr(0xED),  # Ã -> í
    chr(0xC3)+chr(0xB3): chr(0xF3),  # Ã³ -> ó
    chr(0xC3)+chr(0xBA): chr(0xFA),  # Ãº -> ú
    chr(0xC3)+chr(0xA2): chr(0xE2),  # Ã¢ -> â
    chr(0xC3)+chr(0xAA): chr(0xEA),  # Ãª -> ê
    chr(0xC3)+chr(0xB4): chr(0xF4),  # Ã´ -> ô
    chr(0xC3)+chr(0xA0): chr(0xE0),  # Ã  -> à
    chr(0xC3)+chr(0xA7): chr(0xE7),  # Ã§ -> ç
    chr(0xC3)+chr(0x87): chr(0xC7),  # Ã‡ -> Ç
    chr(0xC3)+chr(0x95): chr(0xD5),  # Ã• -> Õ
    chr(0xC3)+chr(0xB5): chr(0xF5),  # Ãµ -> õ
    chr(0xC3)+chr(0x81): chr(0xC1),  # Ã -> Á
    chr(0xC3)+chr(0x8D): chr(0xCD),  # Ã\x8d -> Í
    chr(0xC3)+chr(0x93): chr(0xD3),  # Ã“ -> Ó
    chr(0xC3)+chr(0x94): chr(0xD4),  # Ã” -> Ô
    chr(0xC3)+chr(0x8A): chr(0xCA),  # ÃŠ -> Ê
    chr(0xC3)+chr(0x80): chr(0xC0),  # Ã€ -> À
    chr(0xC3)+chr(0x9C): chr(0xDC),  # Ãœ -> Ü
    chr(0xC3)+chr(0x9F): chr(0xDF),  # ÃŸ -> ß
    # 2 niveis (mojibake duplo)
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA7): chr(0xE7),  # ÃƒÂ§ -> ç
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA3): chr(0xE3),  # ÃƒÂ£ -> ã
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA1): chr(0xE1),  # ÃƒÂ¡ -> á
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA9): chr(0xE9),  # ÃƒÂ© -> é
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xAD): chr(0xED),  # ÃƒÂ -> í
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xB3): chr(0xF3),  # ÃƒÂ³ -> ó
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xBA): chr(0xFA),  # ÃƒÂº -> ú
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xA2): chr(0xE2),  # ÃƒÂ¢ -> â
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xAA): chr(0xEA),  # ÃƒÂª -> ê
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0xB4): chr(0xF4),  # ÃƒÂ´ -> ô
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x87): chr(0xC7),  # ÃƒÂ‡ -> Ç
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x95): chr(0xD5),  # ÃƒÂ• -> Õ
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x8D): chr(0xCD),  # ÃƒÂ\x8d -> Í
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x93): chr(0xD3),  # ÃƒÂ“ -> Ó
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x94): chr(0xD4),  # ÃƒÂ” -> Ô
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x8A): chr(0xCA),  # ÃƒÂŠ -> Ê
    chr(0xC3)+chr(0x83)+chr(0xC2)+chr(0x81): chr(0xC1),  # ÃƒÂ -> Á
    # Casos especiais (mojibake triplo)
    chr(0xC3)+chr(0x83)+chr(0x86)+chr(0x92): chr(0xC3),  # ÃƒÆ’ -> Ã (residual)
    chr(0xC3)+chr(0x83)+chr(0x86)+chr(0xE2)+chr(0x80)+chr(0x99): chr(0xC7),  # ÃƒÆ’â€™ -> Ç
}

alteradas = 0
linhas_novas = []

for i, ln in enumerate(c.split("\n"), 1):
    original = ln
    # Remove soft hyphen e caracteres de controle que nao tem mapeamento
    ln_limpa = ln.replace(chr(0xAD), "")  # soft hyphen
    # Aplica mapa de substituicoes
    for antigo, novo in mapa.items():
        if antigo in ln_limpa:
            ln_limpa = ln_limpa.replace(antigo, novo)
    if ln_limpa != original:
        alteradas += 1
        if alteradas <= 15:
            print(f"[{i}] {repr(original.strip()[:70])}")
            print(f"     -> {repr(ln_limpa.strip()[:70])}")
    linhas_novas.append(ln_limpa)

c_novo = "\n".join(linhas_novas)
open(back_path, "w", encoding="utf-8").write(c_novo)

print(f"\n[OK] {alteradas} linhas corrigidas.")

# Valida
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_2niveis_{ts}", back_path)
    print("[OK] Backup restaurado.")
