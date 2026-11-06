import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_seguro_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

inicio = c.find('elif tipo == "DMPL":')
if inicio == -1:
    print("[ERRO] Bloco DMPL não encontrado.")
    exit(1)

fim = c.find('else:', inicio + 10)
if fim == -1:
    print("[ERRO] Fim do bloco DMPL não encontrado.")
    exit(1)

bloco_antigo = c[inicio:fim]

# Substitui a função buscar_valores por regex (mais seguro)
padrao = r'def buscar_valores\(termo\):.*?return "", ""'
if re.search(padrao, bloco_antigo, re.DOTALL):
    novo_bloco = re.sub(padrao, 
        '''def buscar_valores(termo):
                def normalizar(s):
                    return s.encode('ascii', 'ignore').decode('ascii').upper().strip()
                termo_norm = normalizar(termo)
                for linha in content.splitlines():
                    if normalizar(linha[:100]).startswith(termo_norm):
                        colunas = linha.split(';')
                        val1 = colunas[7].strip() if len(colunas) > 7 else ""
                        val2 = colunas[8].strip() if len(colunas) > 8 else ""
                        return val1, val2
                return "", ""''',
        bloco_antigo, count=1, flags=re.DOTALL)
    
    # Também corrige a ordem das buscas (período antes de exercício)
    novo_bloco = novo_bloco.replace(
        'res_1, res_2 = buscar_valores("Resultado do perÃodo")',
        'res_1, res_2 = buscar_valores("Resultado do perÃodo")\n            if not res_1 and not res_2:\n                res_1, res_2 = buscar_valores("Resultado do exercÃcio")'
    )
    
    c = c[:inicio] + novo_bloco + c[fim:]
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Bloco DMPL corrigido (mantendo o draw_row)!")
else:
    print("[AVISO] Função buscar_valores não encontrada.")

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_seguro_{ts}", back_path)
    print("[OK] Backup restaurado")
