import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_ordem_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza o bloco do DMPL
inicio = c.find('elif tipo == "DMPL":')
if inicio == -1:
    print("[ERRO] Bloco DMPL não encontrado.")
    exit(1)

fim = c.find('else:', inicio + 10)
if fim == -1:
    print("[ERRO] Fim do bloco DMPL não encontrado.")
    exit(1)

bloco = c[inicio:fim]

# Substitui a busca para procurar "Resultado do período" primeiro
# e só depois "Resultado do exercício"
antigo = '''res_1, res_2 = buscar_valores("Resultado do perÃodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercÃcio")'''

# Tenta variação 1
if antigo not in bloco:
    antigo = '''res_1, res_2 = buscar_valores("Resultado do perÃodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercÃcio")'''

novo = '''res_1, res_2 = buscar_valores("Resultado do perÃodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercÃcio")'''

# Se a string não foi encontrada, tenta regex
if antigo in bloco:
    bloco = bloco.replace(antigo, novo, 1)
    print("[OK] Ordem das buscas corrigida (período antes de exercício).")
else:
    # Tenta regex para encontrar e substituir a linha de busca
    padrao = r'res_1, res_2 = buscar_valores\("Resultado do per.*?exerc.*?\)'
    if re.search(padrao, bloco):
        bloco = re.sub(padrao, 
            'res_1, res_2 = buscar_valores("Resultado do perÃodo")\n            if not res_1 and not res_2:\n                res_1, res_2 = buscar_valores("Resultado do exercÃcio")',
            bloco, count=1)
        print("[OK] Ordem das buscas corrigida via regex.")
    else:
        print("[AVISO] Não foi possível encontrar a busca para corrigir.")

c = c[:inicio] + bloco + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_ordem_{ts}", back_path)
    print("[OK] Backup restaurado")
