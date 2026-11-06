import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_direto_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

inicio = c.find('elif tipo == "DMPL":')
if inicio == -1:
    print("[ERRO] Bloco DMPL não encontrado.")
    exit(1)

fim = c.find('else:', inicio + 10)
if fim == -1:
    print("[ERRO] Fim do bloco DMPL não encontrado.")
    exit(1)

bloco = c[inicio:fim]

# Encontra todas as linhas que chamam buscar_valores
linhas_busca = re.findall(r'res_1, res_2 = buscar_valores\("([^"]+)"\)', bloco)
print(f"[INFO] Buscas atuais encontradas: {linhas_busca}")

# Substitui a ordem: busca "Resultado do periodo" (sem acento) primeiro
# Vamos usar regex para pegar qualquer variação de "Resultado do ..." e substituir
padrao = r'res_1, res_2 = buscar_valores\("Resultado[^"]*"\)'

if re.search(padrao, bloco):
    bloco = re.sub(padrao, 
        'res_1, res_2 = buscar_valores("Resultado do perÃodo")\n            if not res_1 and not res_2:\n                res_1, res_2 = buscar_valores("Resultado do exercÃcio")',
        bloco, count=1)
    print("[OK] Ordem das buscas corrigida (período antes de exercício).")
else:
    print("[AVISO] Não foi possível encontrar a chamada de buscar_valores.")

c = c[:inicio] + bloco + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_direto_{ts}", back_path)
    print("[OK] Backup restaurado")
