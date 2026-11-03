import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_porta_custo_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a porta 9999 para 9994 na rota de PDF do custo pessoal
c_antigo = 'http://127.0.0.1:9999/'
c_novo = 'http://127.0.0.1:9994/'

if c_antigo in c:
    # Substitui apenas nas URLs que contém custo_pessoal para não afetar outras coisas
    c = re.sub(r'http://127\.0\.0\.1:9999/(custo_pessoal[^\"]*)', r'http://127.0.0.1:9994/\1', c)
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Porta corrigida de 9999 para 9994 nas rotas de Custo Pessoal!")
else:
    print("[AVISO] URL com a porta 9999 não encontrada. Talvez já tenha sido corrigida.")

# Valida a sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
