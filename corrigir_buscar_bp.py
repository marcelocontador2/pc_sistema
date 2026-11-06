import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_verif_bp_final_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao buscar no contexto da verificacao do BP
antigo = '''        def buscar(linhas, termos, coluna):
            for p in linhas:
                for celula in p:
                    for termo in termos:
                        if termo.upper() in str(celula).upper():
                            if len(p) > coluna:
                                try:
                                    v = abs(_limpar_valor(p[coluna]))
                                    if v > 0:
                                        return v
                                except:
                                    pass
            return 0.0'''

novo = '''        def buscar(linhas, termos, coluna):
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

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Funcao buscar corrigida: pega o valor da coluna seguinte.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta encontrar a funcao buscar em qualquer lugar
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
    shutil.copy2(f"{back_path}.bak_verif_bp_final_{ts}", back_path)
