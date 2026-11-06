import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_ascii_safe_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

def tentar_decodificar(trecho):
    """Tenta decodificar mojibake ate virar 1 caractere unico (qualquer um)."""
    atual = trecho
    for _ in range(8):
        try:
            dec = atual.encode("latin-1").decode("utf-8")
            if dec != atual:
                atual = dec
                if len(atual) == 1:
                    return atual
                continue
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        try:
            dec = atual.encode("cp1252").decode("utf-8")
            if dec != atual:
                atual = dec
                if len(atual) == 1:
                    return atual
                continue
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        break
    return None

# Regex: sequencias de 2 a 8 caracteres nao-ASCII
padrao = re.compile(r'[^\x00-\x7F]{2,8}')

def corrigir_linha(ln):
    def repl(m):
        resultado = tentar_decodificar(m.group())
        return resultado if resultado else m.group()
    return padrao.sub(repl, ln)

alteradas = 0
for i in range(len(linhas)):
    if 315 <= i <= 319:
        continue
    original = linhas[i]
    nova = corrigir_linha(original)
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
    shutil.copy2(f"main.py.bak_ascii_safe_{ts}", "main.py")
    print("[OK] Backup restaurado.")
