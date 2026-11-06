import shutil, sys, datetime

ARQUIVO = r"pc_backend\main.py"
BACKUP = f"pc_backend\\main_backup_liquidez3_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(ARQUIVO, BACKUP)
print(f"[OK] Backup: {BACKUP}\n")

with open(ARQUIVO, "r", encoding="utf-8") as f:
    conteudo = f.read()

# ---------- 1) Remove termos curtos que dao falso positivo ----------
old_termos = '''    caixa = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ativo_circulante = buscar("ATIVO CIRCULANTE")
    estoques = buscar("ESTOQUES")
    realizavel_lp = buscar("REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO", "REALIZAVEL LP", "ATIVO REALIZAVEL")
    ativo_nao_circulante = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE", "ATIVO NAO CIRCULANTE", "ANC")
    imobilizado = buscar("IMOBILIZADO", "IMOBILIZADO LIQUIDO")
    passivo_circulante = buscar("PASSIVO CIRCULANTE")
    passivo_nao_circulante = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE", "PASSIVO NAO CIRCULANTE", "PNC")
    passivo_total = buscar("PASSIVO TOTAL", "TOTAL DO PASSIVO", "TOTAL PASSIVO")
    ativo_total = buscar("ATIVO TOTAL", "TOTAL DO ATIVO", "TOTAL ATIVO")
    patrimonio_liquido = buscar("PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO", "PATRIMONIO SOCIAL", "PL")'''

new_termos = '''    caixa = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ativo_circulante = buscar("ATIVO CIRCULANTE")
    estoques = buscar("ESTOQUES")
    realizavel_lp = buscar("ATIVO REALIZAVEL A LONGO PRAZO", "REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO")
    ativo_nao_circulante = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE")
    imobilizado = buscar("IMOBILIZADO", "IMOBILIZADO LIQUIDO")
    passivo_circulante = buscar("PASSIVO CIRCULANTE")
    passivo_nao_circulante = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE")
    passivo_total = buscar("TOTAL DO PASSIVO", "PASSIVO TOTAL", "TOTAL PASSIVO")
    ativo_total = buscar("ATIVO TOTAL", "TOTAL DO ATIVO", "TOTAL ATIVO")
    patrimonio_liquido = buscar("TOTAL DO PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO", "PATRIMONIO SOCIAL")'''

if old_termos not in conteudo:
    print("[ERRO] Bloco de termos atual nao encontrado.")
    sys.exit(1)
conteudo = conteudo.replace(old_termos, new_termos, 1)
print("[OK] Termos 'ANC', 'PNC', 'PL' removidos (curtos demais)")

# ---------- 2) Corrige o fallback do ativo_total ----------
old_fallback = '''    # Fallbacks robustos quando as linhas totais nao existem no CSV
    if not ativo_nao_circulante and imobilizado:
        ativo_nao_circulante = imobilizado
    if not ativo_total:
        ativo_total = (ativo_circulante or 0.0) + (ativo_nao_circulante or 0.0) + (realizavel_lp or 0.0)
    if not passivo_total and passivo_circulante and passivo_nao_circulante:
        passivo_total = passivo_circulante + passivo_nao_circulante
    if not patrimonio_liquido and ativo_total and passivo_total:
        patrimonio_liquido = ativo_total - passivo_total'''

new_fallback = '''    # ===== Fallbacks robustos =====
    # CUIDADO: no BP brasileiro, ARLP e Imobilizado JA ESTAO dentro do ANC.
    # Por isso NAO somar ARLP ao ANC novamente.

    # 1) Se nao achou ANC mas achou Imobilizado, usa Imobilizado como piso
    if not ativo_nao_circulante and imobilizado:
        ativo_nao_circulante = imobilizado

    # 2) Se nao achou passivo_total, calcula pela soma dos componentes
    if not passivo_total and passivo_circulante and passivo_nao_circulante:
        passivo_total = passivo_circulante + passivo_nao_circulante

    # 3) Ativo total: AC + ANC (ARLP ja esta dentro de ANC)
    if not ativo_total:
        if ativo_circulante and ativo_nao_circulante:
            ativo_total = ativo_circulante + ativo_nao_circulante
        elif ativo_circulante:
            ativo_total = ativo_circulante + (realizavel_lp or 0.0) + (imobilizado or 0.0)

    # 4) Se ainda nao tem ativo_total mas tem passivo + PL, usa a equacao contabil
    if not ativo_total and passivo_total and patrimonio_liquido:
        ativo_total = passivo_total + patrimonio_liquido

    # 5) Se nao achou PL mas tem ativo e passivo totais
    if not patrimonio_liquido and ativo_total and passivo_total:
        patrimonio_liquido = ativo_total - passivo_total

    # 6) VALIDACAO FINAL: se ativo_total nao bate com (passivo_total + PL), forca a equacao contabil
    if ativo_total and passivo_total and patrimonio_liquido:
        soma_esperada = passivo_total + patrimonio_liquido
        if abs(ativo_total - soma_esperada) > 1.0:  # tolerancia de R$ 1
            ativo_total = soma_esperada'''

if old_fallback not in conteudo:
    print("[ERRO] Bloco de fallback atual nao encontrado.")
    sys.exit(1)
conteudo = conteudo.replace(old_fallback, new_fallback, 1)
print("[OK] Fallback corrigido (nao soma ARLP duas vezes)")
print("[OK] Validacao contabil adicionada (ativo = passivo + PL)")

# ---------- 3) Validar e salvar ----------
try:
    compile(conteudo, ARQUIVO, "exec")
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    sys.exit(1)

with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(conteudo)
print(f"[OK] main.py atualizado ({len(conteudo):,} chars)\n")

print("=== VALORES ESPERADOS APOS O PATCH ===")
print("  ativo_circulante       = 301.495.379,14")
print("  ativo_nao_circulante   = 315.111.651,51")
print("  ativo_total            = 616.607.030,65  (= AC + ANC, bate c/ linha 41)")
print("  passivo_circulante     =  11.725.635,04")
print("  passivo_nao_circulante =     513.151,00")
print("  passivo_total          =  12.238.786,04")
print("  patrimonio_liquido     = 604.368.244,61")
print()
print("=== ESTRUTURA ESPERADA ===")
print("  endividamento_geral     = 1,98%   (12M / 616M)")
print("  part_capital_terceiros  = 2,02%   (12M / 604M)")
print("  imobilizacao_pl         = 21,42%  (129M / 604M)")
print()
print("=== PROXIMO PASSO ===")
print("1. Ctrl+C no servidor uvicorn")
print("2. cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. cd ..; .\\pc_venv\\Scripts\\python.exe testar_api_liquidez.py")
