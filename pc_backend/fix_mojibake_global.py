import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_mojibake_{ts}")

c = open(back_path, encoding="utf-8-sig").read()
linhas_orig = c.split("\n")
linhas_novas = []
alteradas = 0

def desfazer_mojibake(s):
    """Reverte mojibake (UTF-8 lido como Latin-1) recursivamente."""
    anterior = None
    atual = s
    # Maximo 5 iteracoes para evitar loop
    for _ in range(5):
        if anterior == atual:
            break
        anterior = atual
        try:
            # Tenta Latin-1 -> UTF-8
            atual = atual.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return atual

for i, ln in enumerate(linhas_orig, 1):
    # So processa linhas com mojibake detectavel
    if "Ã" in ln or "\xad" in ln or "\x8d" in ln or "\x9d" in ln:
        try:
            nova = desfazer_mojibake(ln)
            # Remove soft hyphen (\xad) remanescente
            nova = nova.replace("\xad", "")
            if nova != ln:
                linhas_novas.append(nova)
                alteradas += 1
                if alteradas <= 10:
                    print(f"[{i}] {repr(ln.strip()[:80])}")
                    print(f"     -> {repr(nova.strip()[:80])}")
                continue
        except Exception:
            pass
    linhas_novas.append(ln)

c_novo = "\n".join(linhas_novas)
open(back_path, "w", encoding="utf-8").write(c_novo)

print(f"\n[OK] {alteradas} linhas corrigidas.")

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_mojibake_{ts}", back_path)
    print("[OK] Backup restaurado.")
