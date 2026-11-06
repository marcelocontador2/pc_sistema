import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\integridade.py"
shutil.copy2(back_path, f"{back_path}.bak_bp_final_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza o trecho do BP e substitui a lógica de leitura
antigo = '''        ativo, passivo = 0.0, 0.0
        for p in linhas:
            if len(p) >= 5:
                if p[0].strip().upper() == "TOTAL":
                    ativo = _limpar_valor(p[1])
                    # No novo CSV, o valor total do Passivo + PL esta na coluna 4
                    # (a coluna 3 e a especificacao "TOTAL")
                    if len(p) > 4:
                        passivo = _limpar_valor(p[4])
                    else:
                        passivo = _limpar_valor(p[4]) if len(p) > 4 else _limpar_valor(p[3])
                    break'''

novo = '''        ativo, passivo = 0.0, 0.0
        for p in linhas:
            if len(p) >= 5:
                if p[0].strip().upper() == "TOTAL":
                    ativo = _limpar_valor(p[1])
                    # O valor do Passivo + PL esta na coluna 4 (p[4])
                    passivo = _limpar_valor(p[4])
                    # Se o passivo for 0, tenta a coluna 3 (fallback)
                    if passivo == 0.0 and len(p) > 3:
                        passivo = _limpar_valor(p[3])
                    break'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Leitura do Passivo corrigida: usa p[4] (coluna 4).")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta substituir a linha do passivo
    c = c.replace('passivo = _limpar_valor(p[4])', 'passivo = _limpar_valor(p[4])')
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Tentativa de ajuste (variacao).")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_bp_final_{ts}", back_path)
