import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_linha949_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Corrige a chamada na linha 949
antigo = 'passivo_total = buscar(l_bp, "TOTAL", 3)'
novo = 'passivo_total = buscar(l_bp, ["TOTAL"], 3)'

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Chamada da linha 949 corrigida (string -> lista).")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta encontrar qualquer chamada com "TOTAL" (string) em vez de lista
    padrao = re.compile(r'buscar\(l_bp, "TOTAL", 3\)')
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(0), 'buscar(l_bp, ["TOTAL"], 3)')
        open(back_path, "w", encoding="utf-8").write(c)
        print("[OK] Chamada corrigida (variacao).")
    else:
        print("[ERRO] Nao foi possivel encontrar a chamada.")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_linha949_{ts}", back_path)
