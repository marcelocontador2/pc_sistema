import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_calc_panorama_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao buscar dentro de _calc_panorama
antigo = '''    def buscar(linhas, termo, coluna):
        for p in linhas:
            if len(p) > coluna and termo.upper() in p[0].upper():
                return abs(_limpar_valor(p[coluna]))
        return 0.0'''

novo = '''    def buscar(linhas, termo, coluna):
        # Procura o termo na coluna 0 (Ativo) ou 3 (Passivo)
        # e pega o valor da coluna seguinte (1 para Ativo, 4 para Passivo)
        termo_upper = termo.upper() if isinstance(termo, str) else termo[0].upper()
        for p in linhas:
            for col_espec in [0, 3]:
                if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
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
    print("[OK] Funcao buscar de _calc_panorama corrigida.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    padrao = re.compile(r'def buscar\(linhas, termo, coluna\):.*?return 0\.0', re.DOTALL)
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
    shutil.copy2(f"{back_path}.bak_calc_panorama_{ts}", back_path)
