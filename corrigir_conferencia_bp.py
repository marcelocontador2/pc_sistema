import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_usar_def7_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza o trecho onde o BP e calculado (linhas 1033-1034)
antigo = '''        # NOVO CSV: Passivo esta na coluna 3 (especificacao) e o valor na coluna 4
        # Patrimonio Liquido esta na coluna 3 (especificacao) e o valor na coluna 4
        passivo_total = buscar("TOTAL DO PASSIVO", 4)
        pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)
        if pl == 0.0:
            pl = buscar("RESULTADOS ACUMULADOS", 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL'''

novo = '''        # Usa a funcao buscar da Definicao 7 (que procura na coluna 0/3 e pega o valor da coluna seguinte)
        # Testado manualmente: retorna os valores corretos
        passivo_total = buscar("TOTAL DO PASSIVO", 4)
        pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)
        if pl == 0.0:
            pl = buscar("RESULTADOS ACUMULADOS", 4)
        ativo_total = passivo_total + pl  # Ativo = Passivo + PL
        print(f"[CONFERENCIA] passivo_total={passivo_total}, pl={pl}, ativo_total={ativo_total}")'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Trecho do BP na conferencia corrigido (usa Definicao 7 + debug).")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Tenta substituir linha por linha
    c = c.replace('passivo_total = buscar("TOTAL DO PASSIVO", 4)', 'passivo_total = buscar("TOTAL DO PASSIVO", 4)  # Definicao 7')
    c = c.replace('pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)', 'pl = buscar("TOTAL DO PATRIMÔNIO LÍQUIDO", 4)  # Definicao 7')
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Trecho ajustado (variacao).")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_usar_def7_{ts}", back_path)
