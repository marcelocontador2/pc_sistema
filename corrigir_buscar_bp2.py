import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_buscar_bp2_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao buscar no contexto da verificacao do BP
antigo = '''        def buscar(linhas, termos, coluna):
            for p in linhas:
                for i, celula in enumerate(p):
                    for termo in termos:
                        if termo.upper() in str(celula).upper():
                            # Pega o valor da coluna seguinte a onde encontrou o termo
                            prox_coluna = i + 1
                            if len(p) > prox_coluna:
                                try:
                                    v = abs(_limpar_valor(p[prox_coluna]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0'''

novo = '''        def buscar(linhas, termos, coluna):
            for p in linhas:
                for termo in termos:
                    termo_upper = termo.upper()
                    # Procura o termo na coluna de especificacao (0 para Ativo, 2 para Passivo)
                    for col_espec in [0, 2]:
                        if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                            # Pega o valor da coluna seguinte (1 ou 3)
                            col_valor = col_espec + 1
                            if len(p) > col_valor:
                                try:
                                    v = abs(_limpar_valor(p[col_valor]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Funcao buscar corrigida: procura na coluna 0/2 e pega valor na 1/3.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    padrao = re.compile(r'def buscar\(linhas, termos, coluna\):.*?return 0\.0', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(0), novo)
        open(back_path, "w", encoding="utf-8").write(c)
        print("[OK] Funcao buscar corrigida (variacao).")
    else:
        print("[ERRO] Nao foi possivel encontrar a funcao buscar.")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_buscar_bp2_{ts}", back_path)
