import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_chamada_def7_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Corrige as chamadas da linha 1033 e 1034 para usar a Definição 7 corretamente
antigo = '''        passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 4)
        pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO", "RESULTADOS ACUMULADOS"], 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL'''

novo = '''        # Usa a Definição 7 (que procura na coluna 0/3 e pega o valor da coluna seguinte)
        passivo_total = buscar("TOTAL DO PASSIVO", 4)
        pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)
        if pl == 0.0:
            pl = buscar("RESULTADOS ACUMULADOS", 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Chamadas corrigidas: agora usam a Definicao 7 (string, coluna).")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta substituir linha por linha
    c = c.replace('passivo_total = buscar(l_bp, ["TOTAL DO PASSIVO"], 4)', 'passivo_total = buscar("TOTAL DO PASSIVO", 4)')
    c = c.replace('pl = buscar(l_bp, ["TOTAL DO PATRIMÔNIO LÍQUIDO", "TOTAL DO PATRIMONIO LIQUIDO", "RESULTADOS ACUMULADOS"], 4)', 'pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)')
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Chamadas corrigidas (variacao).")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_chamada_def7_{ts}", back_path)
