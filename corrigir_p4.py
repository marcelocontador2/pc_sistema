import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\integridade.py"
shutil.copy2(back_path, f"{back_path}.bak_bp_p4_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a linha exata "passivo = _limpar_valor(p[3])"
antigo = 'passivo = _limpar_valor(p[3])'
novo = 'passivo = _limpar_valor(p[4]) if len(p) > 4 else _limpar_valor(p[3])'

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Linha do passivo corrigida: p[3] -> p[4].")
else:
    print("[AVISO] Linha exata nao encontrada. Tentando regex...")
    # Tenta encontrar qualquer linha que atribua passivo a partir de p[3]
    padrao = re.compile(r'passivo\s*=\s*_limpar_valor\(p\[3\]\)')
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(0), novo)
        open(back_path, "w", encoding="utf-8").write(c)
        print("[OK] Linha corrigida via regex.")
    else:
        print("[ERRO] Nao foi possivel encontrar a linha do passivo.")
        # Mostra as linhas que contem "passivo"
        for i, ln in enumerate(c.split("\n"), 1):
            if 'passivo' in ln.lower():
                print(f"  Linha {i}: {ln.strip()[:150]}")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_bp_p4_{ts}", back_path)
