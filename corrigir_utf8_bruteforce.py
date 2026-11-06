import re, shutil, datetime, os, glob

# 1. Restaura o main.py do backup mais antigo que NÃO tem a fonte quebrada
backups = glob.glob(r"pc_backend\main_backup_utf8_fix_*.py")
if not backups:
    print("[ERRO] Backup não encontrado.")
    exit()
backup = min(backups, key=os.path.getctime)  # o mais antigo = estado antes da tentativa falha
print(f"[OK] Restaurando de: {backup}")
shutil.copy2(backup, r"pc_backend\main.py")

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

fonte_ok = "C:/Windows/Fonts/arial.ttf"
if not os.path.exists(fonte_ok):
    print("[ERRO] arial.ttf não encontrado.")
    exit()
print(f"[INFO] Fonte: {fonte_ok}")

# 2. Para cada função, encontra o bloco e injeta o add_font + troca Helvetica
def corrigir_funcao(nome_funcao, regex_rota):
    global main_code
    padrao = re.compile(regex_rota, re.DOTALL)
    match = padrao.search(main_code)
    if not match:
        print(f"[AVISO] {nome_funcao} não encontrada.")
        return
    
    bloco = match.group(0)
    bloco_orig = bloco
    
    # 2a. Injetar add_font logo após "pdf = FPDF(" (aceita qualquer variação)
    padrao_fpdf = re.compile(r'(pdf\s*=\s*FPDF\s*\([^)]*\))')
    if padrao_fpdf.search(bloco):
        injecao = (
            r'\1\n'
            + f'    pdf.add_font("DejaVu", "", r"{fonte_ok}", uni=True)\n'
            + f'    pdf.add_font("DejaVu", "B", r"{fonte_ok}", uni=True)\n'
            + f'    pdf.add_font("DejaVu", "I", r"{fonte_ok}", uni=True)'
        )
        bloco = padrao_fpdf.sub(injecao, bloco, count=1)
    
    # 2b. Trocar a variável fonte_padrao (BF)
    bloco = bloco.replace('fonte_padrao = "Helvetica"', 'fonte_padrao = "DejaVu"')
    
    # 2c. Trocar todas as chamadas set_font("Helvetica", ...) (DFC)
    bloco = re.sub(r'set_font\(\s*"Helvetica"\s*,', 'set_font("DejaVu",', bloco)
    
    if bloco != bloco_orig:
        main_code = main_code.replace(bloco_orig, bloco)
        print(f"[OK] {nome_funcao} corrigida.")
    else:
        print(f"[AVISO] {nome_funcao}: nenhuma substituição feita.")

# Aplica nas duas funções
corrigir_funcao("BF", r'@app\.get\("/gerar_pdf_analise_financeira_bf/\{id\}"\).*?(?=\n@app\.|\Z)')
corrigir_funcao("DFC", r'@app\.get\("/gerar_pdf_analise_dfc/\{id\}"\).*?(?=\n@app\.|\Z)')

# 3. Valida a sintaxe
try:
    compile(main_code, r"pc_backend\main.py", "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(r"pc_backend\main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] main.py salvo com sucesso.")
