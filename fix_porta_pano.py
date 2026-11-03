import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_porta_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a porta de 8001 para 9994
c_antigo = 'http://127.0.0.1:8001/api/panorama/'
c_novo = 'http://127.0.0.1:9994/api/panorama/'

if c_antigo in c:
    c = c.replace(c_antigo, c_novo)
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] URL corrigida de :8001 para :9994 na rota de PDF do Panorama!")
else:
    print("[AVISO] URL antiga não encontrada. Talvez já tenha sido corrigida.")

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
