import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_res_periodo_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# A linha 528 atual (com encoding corrompido no literal)
antigo = 'res_1, res_2 = buscar_valores("Resultado do perÃodo")'

# Nova chamada: busca por prefixo robusto, com fallback para "Resultado do periodo" (sem acento)
# e depois "Resultado do exercício" se ainda não achar
novo = '''res_1, res_2 = buscar_valores("Resultado do per")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do periodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exerc")'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Chamada da linha 528 substituída (busca robusta com fallback).")
else:
    # Tenta variação sem o "Ã" corrompido
    antigo2 = 'res_1, res_2 = buscar_valores("Resultado do período")'
    if antigo2 in c:
        c = c.replace(antigo2, novo, 1)
        print("[OK] Chamada (variação acentuada) substituída.")
    else:
        print("[ERRO] Não encontrei a linha 528. Abortando sem alterar.")
        exit(1)

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_res_periodo_{ts}", back_path)
    print("[OK] Backup restaurado")
