import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_titulo_dmpl_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

linhas = c.split('\n')

# Linha 373 (índice 372)
idx = 372
if idx >= len(linhas):
    print(f"[ERRO] Arquivo tem só {len(linhas)} linhas.")
    exit(1)

alvo = linhas[idx]
print(f"[INFO] Linha 373 atual: {repr(alvo)}")

if 'titulo_pdf' not in alvo:
    print("[ERRO] Linha 373 não é a definição de titulo_pdf. Abortando.")
    exit(1)

# Preserva a indentação
indent = ' ' * (len(alvo) - len(alvo.lstrip()))

# Texto correto (UTF-8 normal, sem soft hyphen, sem mojibake)
nova_linha = f'{indent}titulo_pdf = "Demonstração das Mutações do Patrimônio Líquido"'
linhas[idx] = nova_linha

c = '\n'.join(linhas)
open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
    print(f"[OK] Linha 373 corrigida para: {repr(nova_linha.strip())}")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_titulo_dmpl_{ts}", back_path)
    print("[OK] Backup restaurado")
