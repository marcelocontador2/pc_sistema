import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_upload_bp_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Procura o bloco de renomeacao (onde estao COMPARATIVO_RECEITAS, COMPARATIVO_DESPESAS, CENTRO_CUSTOS)
# e adiciona a regra do BALANCO_PATRIMONIAL
antigo = '''    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"'''

novo = '''    if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"CENTRO_CUSTOS_{periodo_str}.csv"
    
    # NOVO: Balanco Patrimonial (inclui Comparativo)
    if tipo_relatorio and ("BALANCO_PATRIMONIAL" in tipo_relatorio.upper() or "BALANÇO PATRIMONIAL" in tipo_relatorio.upper() or "BALANCO PATRIMONIAL" in tipo_relatorio.upper() or "BP" == tipo_relatorio.upper() or "BALANCOPATRIMONIALCOMPARATIVO" in (file.filename or "").upper()):
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"BALANCO_PATRIMONIAL_{periodo_str}.csv"'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Regra de renomeacao do BALANCO_PATRIMONIAL adicionada na rota /upload.")
else:
    print("[AVISO] Bloco de renomeacao nao encontrado. Tentando variacao...")
    # Tenta variacao com aspas diferentes ou indentacao
    padrao = re.compile(r'(if tipo_relatorio and tipo_relatorio\.upper\(\) == "CENTRO_CUSTOS":\s*\n\s*periodo_str = f"\{ano\}_\{periodo_tipo\}_\{periodo_valor\}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"\s*\n\s*nome_arquivo = f"CENTRO_CUSTOS_\{periodo_str\}\.csv")', re.DOTALL)
    match = padrao.search(c)
    if match:
        bloco_antigo = match.group(0)
        bloco_novo = bloco_antigo + '''

    # NOVO: Balanco Patrimonial (inclui Comparativo)
    if tipo_relatorio and ("BALANCO_PATRIMONIAL" in tipo_relatorio.upper() or "BALANÇO PATRIMONIAL" in tipo_relatorio.upper() or "BALANCO PATRIMONIAL" in tipo_relatorio.upper() or "BP" == tipo_relatorio.upper() or "BALANCOPATRIMONIALCOMPARATIVO" in (file.filename or "").upper()):
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"BALANCO_PATRIMONIAL_{periodo_str}.csv"'''
        c = c.replace(bloco_antigo, bloco_novo, 1)
        print("[OK] Regra de renomeacao do BALANCO_PATRIMONIAL adicionada (variacao).")
    else:
        print("[ERRO] Nao foi possivel encontrar o bloco de renomeacao.")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_upload_bp_{ts}", back_path)
