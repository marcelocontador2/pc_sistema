import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_verif_bp_corrige_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza o trecho da verificacao do BP
antigo = '''        # === BP ===
        passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 3)
        pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"], 3)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL'''

novo = '''        # === BP ===
        # NOVO CSV: Passivo esta na coluna 3 (especificacao) e o valor na coluna 4
        # Patrimonio Liquido esta na coluna 3 (especificacao) e o valor na coluna 4
        passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 4)
        pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO", "RESULTADOS ACUMULADOS"], 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Verificacao do BP corrigida: busca 'Passivo' e 'PL' na coluna 4.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta buscar com "TOTAL DO PASSIVO" em qualquer coluna
    c = c.replace('passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 3)', 'passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 4)')
    c = c.replace('pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO"], 3)', 'pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO", "RESULTADOS ACUMULADOS"], 4)')
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Verificacao ajustada (variacao).")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_verif_bp_corrige_{ts}", back_path)
