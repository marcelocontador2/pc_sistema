import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_fix_generico_{ts}")

c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Caracteres latinos que queremos como resultado final
ALVOS = set("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇñÑ")

def tentar_decodificar(trecho):
    """Tenta decodificar um trecho mojibake ate virar 1 char latino."""
    atual = trecho
    for _ in range(6):
        try:
            # Tenta latin-1 -> utf-8
            dec = atual.encode("latin-1").decode("utf-8")
            if dec != atual:
                atual = dec
                if len(atual) == 1 and atual in ALVOS:
                    return atual
                continue
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        try:
            # Tenta cp1252 -> utf-8
            dec = atual.encode("cp1252").decode("utf-8")
            if dec != atual:
                atual = dec
                if len(atual) == 1 and atual in ALVOS:
                    return atual
                continue
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        break
    # Se nao virou 1 char latino, retorna None
    return None

# Regex: sequencias de 2 a 6 caracteres nao-ASCII (mojibake tipico)
padrao = re.compile(r'[^\x00-\x7F]{2,6}')

def corrigir_linha(ln):
    def repl(m):
        resultado = tentar_decodificar(m.group())
        return resultado if resultado else m.group()
    return padrao.sub(repl, ln)

alteradas = 0
for i in range(len(linhas)):
    # PULA as linhas 316-320 (codigo de fix em runtime)
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
    shutil.copy2(f"main.py.bak_fix_generico_{ts}", "main.py")
    print("[OK] Backup restaurado.")
