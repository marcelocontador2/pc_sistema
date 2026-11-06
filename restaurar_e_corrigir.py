import glob, os, shutil, re

# 1. Restaura o main.py do backup anterior à última alteração
backups = glob.glob(r"pc_backend\main_backup_bf_dfc_utf8_*.py")
if not backups:
    print("[ERRO] Backup não encontrado.")
    exit()

backup = max(backups, key=os.path.getctime)
print(f"[OK] Restaurando de: {backup}")
shutil.copy2(backup, r"pc_backend\main.py")
print("[OK] main.py restaurado.")

# 2. Verifica se o servidor sobe agora (compile check)
with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe do main.py válida.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe inválida na linha {e.lineno}: {e.msg}")
    exit()

# 3. Aplica a correção de UTF-8 de forma CIRÚRGICA
# Estratégia: em vez de injetar no try/except, injeta após a criação do FPDF() dentro da função
def corrigir_utf8(nome_funcao, fonte_path):
    global codigo
    
    # Encontra a função
    padrao = re.compile(
        rf'(@app\.get\("/{nome_funcao}/[^"]*"\).*?)(?=\n@app\.|\Z)',
        re.DOTALL
    )
    match = padrao.search(codigo)
    if not match:
        print(f"[AVISO] Função {nome_funcao} não encontrada.")
        return
    
    bloco = match.group(1)
    bloco_orig = bloco
    
    # 3a. Após "pdf = FPDF(...)" injeta as fontes (dento do try, mas logo após a criação)
    padrao_fpdf = re.compile(r'(pdf\s*=\s*FPDF\([^)]*\))')
    if padrao_fpdf.search(bloco):
        injecao = r'\1\n    pdf.add_font("DejaVu", "", r"' + fonte_path.replace('\\', '/') + r'", uni=True)\n    pdf.add_font("DejaVu", "B", r"' + fonte_path.replace('\\', '/') + r'", uni=True)\n    pdf.add_font("DejaVu", "I", r"' + fonte_path.replace('\\', '/') + r'", uni=True)'
        bloco = padrao_fpdf.sub(injecao, bloco, count=1)
    
    # 3b. Substitui "Helvetica" por "DejaVu" (com aspas duplas ou simples)
    bloco = bloco.replace('"Helvetica"', '"DejaVu"')
    bloco = bloco.replace("'Helvetica'", "'DejaVu'")
    
    if bloco != bloco_orig:
        codigo = codigo.replace(bloco_orig, bloco)
        print(f"[OK] UTF-8 injetado em {nome_funcao}.")

# Fonte TTF
fontes = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]
fonte_ok = next((f for f in fontes if os.path.exists(f)), None)

if not fonte_ok:
    print("[ERRO] Nenhuma fonte TTF encontrada.")
    exit()

print(f"[INFO] Fonte: {fonte_ok}")

# Aplica para BF e DFC
corrigir_utf8("gerar_pdf_analise_financeira_bf", fonte_ok)
corrigir_utf8("gerar_pdf_analise_dfc", fonte_ok)

# 4. Salva e valida
try:
    compile(codigo, "main.py", "exec")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe inválida após correção, linha {e.lineno}: {e.msg}")
    print("Restaurando backup...")
    shutil.copy2(backup, r"pc_backend\main.py")
    exit()

with open(r"pc_backend\main.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("[OK] Correção aplicada com sucesso. main.py salvo.")
