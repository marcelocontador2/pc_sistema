import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_ordem_final_{ts}")
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

# Exibe o bloco atual para debug
print("--- BLOCO ATUAL (primeiras 30 linhas) ---")
for ln in bloco.split('\n')[:30]:
    print(ln)

# Substitui a função buscar_valores por uma versão que prioriza "Resultado do período"
nova_busca = '''def buscar_valores(termo):
                def normalizar(s):
                    return s.encode('ascii', 'ignore').decode('ascii').upper().strip()
                termo_norm = normalizar(termo)
                for linha in content.splitlines():
                    if normalizar(linha[:100]).startswith(termo_norm):
                        colunas = linha.split(';')
                        val1 = colunas[7].strip() if len(colunas) > 7 else ""
                        val2 = colunas[8].strip() if len(colunas) > 8 else ""
                        return val1, val2
                return "", ""'''

# Substitui a função buscar_valores usando regex
padrao = r'def buscar_valores\(termo\):.*?return "", ""'
if re.search(padrao, bloco, re.DOTALL):
    bloco = re.sub(padrao, nova_busca, bloco, count=1, flags=re.DOTALL)
    print("[OK] Função buscar_valores atualizada.")

# Força a ordem: busca "Resultado do período" primeiro
# Encontra a chamada de "Resultado do período" e a de "Resultado do exercício"
bloco = re.sub(
    r'res_1, res_2 = buscar_valores\("Resultado do per[^"]*"\)\s*\n\s*if not res_1 and not res_2:\s*\n\s*res_1, res_2 = buscar_valores\("Resultado do exerc[^"]*"\)',
    '''res_1, res_2 = buscar_valores("Resultado do período")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercício")''',
    bloco, count=1
)

c = c[:inicio] + bloco + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_ordem_final_{ts}", back_path)
    print("[OK] Backup restaurado")
