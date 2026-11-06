import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = "pc_backend/app/routers/dfc.py"
shutil.copy2(back_path, f"{back_path}.bak_abs_{ts}")

c = open(back_path, encoding="utf-8", errors="ignore").read()

# Remove o abs() da funcao val
antigo = """    def val(p, idx):
        if p and len(p) > idx:
            return abs(limpar(p[idx]))
        return 0.0"""

novo = """    def val(p, idx):
        if p and len(p) > idx:
            return limpar(p[idx])
        return 0.0"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] abs() removido: valores negativos serao preservados.")
else:
    print("[AVISO] Funcao val nao encontrada. Tentando variacao...")
    # Tenta achar a funcao val por regex
    import re
    padrao = re.compile(r'def val\(p, idx\):.*?return 0\.0', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        open(back_path, "w", encoding="utf-8").write(c)
        print("[OK] Funcao val ajustada via regex.")
    else:
        print("[ERRO] Nao foi possivel encontrar a funcao val.")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_abs_{ts}", back_path)
