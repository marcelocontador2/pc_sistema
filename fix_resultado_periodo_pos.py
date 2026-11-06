import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_res_periodo_pos_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

linhas = c.split('\n')

# Confirma que a linha 528 (índice 527) é a chamada de buscar_valores("Resultado do ...")
idx = 527  # linha 528 em base 1
if idx >= len(linhas):
    print(f"[ERRO] Arquivo tem só {len(linhas)} linhas.")
    exit(1)

alvo = linhas[idx]
print(f"[INFO] Linha 528 atual: {repr(alvo)}")

if 'buscar_valores' not in alvo or 'Resultado' not in alvo:
    print("[ERRO] Linha 528 não é a esperada. Abortando sem alterar.")
    exit(1)

# Substitui por 3 chamadas com fallback (mesma indentação de 12 espaços)
indent = ' ' * (len(alvo) - len(alvo.lstrip()))
nova_linha = (
    f'{indent}res_1, res_2 = buscar_valores("Resultado do per")\n'
    f'{indent}if not res_1 and not res_2:\n'
    f'{indent}    res_1, res_2 = buscar_valores("Resultado do periodo")\n'
    f'{indent}if not res_1 and not res_2:\n'
    f'{indent}    res_1, res_2 = buscar_valores("Resultado do exerc")'
)
linhas[idx] = nova_linha

c = '\n'.join(linhas)
open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
    print("[OK] Linha 528 substituída por busca robusta com fallback.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_res_periodo_pos_{ts}", back_path)
    print("[OK] Backup restaurado")
