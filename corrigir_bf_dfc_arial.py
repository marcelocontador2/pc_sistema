import re, shutil, datetime, os, glob

# 1. Restaura o main.py do backup mais recente ANTES das tentativas de UTF-8
backups = glob.glob(r"pc_backend\main_backup_latin1_*.py")
if not backups:
    backups = glob.glob(r"pc_backend\main_backup_*.py")
backup = max(backups, key=os.path.getctime)
print(f"[OK] Restaurando de: {backup}")
shutil.copy2(backup, r"pc_backend\main.py")

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Valida backup
try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe original válida.")
except SyntaxError as e:
    print(f"[ERRO] Backup quebrado na linha {e.lineno}: {e.msg}")
    exit()

fonte = "C:/Windows/Fonts/arial.ttf"

# =========================================================
# 2. Corrigir apenas a função BF
# =========================================================
# Encontra o bloco da função BF
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
bloco_bf = codigo[idx_bf:fim_bf]
bloco_bf_orig = bloco_bf

# 2a. Trocar fonte_padrao = "Helvetica" -> "ArialUnicode"
bloco_bf = bloco_bf.replace('fonte_padrao = "Helvetica"', 'fonte_padrao = "ArialUnicode"')

# 2b. Inserir add_font após "pdf = FPDF()"
padrao_fpdf = re.compile(r'(pdf\s*=\s*FPDF\(\))')
if padrao_fpdf.search(bloco_bf):
    # Injeta as 3 linhas de add_font com indentação de 8 espaços (padrão dentro do try)
    injecao = (
        r'\1\n'
        f'        pdf.add_font("ArialUnicode", "", r"{fonte}", uni=True)\n'
        f'        pdf.add_font("ArialUnicode", "B", r"{fonte}", uni=True)\n'
        f'        pdf.add_font("ArialUnicode", "I", r"{fonte}", uni=True)'
    )
    bloco_bf = padrao_fpdf.sub(injecao, bloco_bf, count=1)
    print("[OK] BF: add_font injetado.")
else:
    print("[AVISO] BF: pdf = FPDF() não encontrado.")

# Substitui o bloco no código
if bloco_bf != bloco_bf_orig:
    codigo = codigo[:idx_bf] + bloco_bf + codigo[fim_bf:]
    print("[OK] BF corrigido.")

# =========================================================
# 3. Corrigir apenas a função DFC
# =========================================================
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
bloco_dfc = codigo[idx_dfc:fim_dfc]
bloco_dfc_orig = bloco_dfc

# 3a. Inserir add_font após pdf = FPDF(orientation=...)
padrao_fpdf_dfc = re.compile(r'(pdf\s*=\s*FPDF\([^)]*\))')
if padrao_fpdf_dfc.search(bloco_dfc):
    # O DFC não está dentro de try, então indentação é 4 espaços
    injecao = (
        r'\1\n'
        f'    pdf.add_font("ArialUnicode", "", r"{fonte}", uni=True)\n'
        f'    pdf.add_font("ArialUnicode", "B", r"{fonte}", uni=True)\n'
        f'    pdf.add_font("ArialUnicode", "I", r"{fonte}", uni=True)'
    )
    bloco_dfc = padrao_fpdf_dfc.sub(injecao, bloco_dfc, count=1)
    print("[OK] DFC: add_font injetado.")
else:
    print("[AVISO] DFC: pdf = FPDF(...) não encontrado.")

# 3b. Trocar "Helvetica" por "ArialUnicode" em TODAS as set_font do DFC
bloco_dfc = re.sub(
    r'set_font\(\s*"Helvetica"\s*,',
    'set_font("ArialUnicode",',
    bloco_dfc
)
print("[OK] DFC: set_font substituído.")

if bloco_dfc != bloco_dfc_orig:
    codigo = codigo[:idx_dfc] + bloco_dfc + codigo[fim_dfc:]
    print("[OK] DFC corrigido.")

# =========================================================
# 4. Validação final
# =========================================================
try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(r"pc_backend\main.py", "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo.")
