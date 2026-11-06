import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_utf8_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Fonte TTF
fontes = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]
fonte_ok = next((f for f in fontes if os.path.exists(f)), None)
if not fonte_ok:
    print("[ERRO] Nenhuma fonte TTF encontrada.")
    exit()
print(f"[INFO] Fonte: {fonte_ok}")

# =========================================================
# 1. BF: substituir fonte_padrao e adicionar add_font
# =========================================================
padrao_bf = re.compile(
    r'(@app\.get\("/gerar_pdf_analise_financeira_bf/\{id\}"\).*?)(?=\n@app\.|\Z)',
    re.DOTALL
)
match_bf = padrao_bf.search(main_code)
if match_bf:
    bloco_bf = match_bf.group(1)
    bloco_bf_orig = bloco_bf

    # 1a. Trocar a definição de fonte_padrao
    bloco_bf = bloco_bf.replace('fonte_padrao = "Helvetica"', 'fonte_padrao = "DejaVu"')

    # 1b. Injetar add_font logo após "pdf = FPDF()"
    padrao_fpdf_bf = re.compile(r'(pdf\s*=\s*FPDF\(\))')
    if padrao_fpdf_bf.search(bloco_bf):
        injecao = r'\1\n        pdf.add_font("DejaVu", "", r"' + fonte_ok.replace('\\','/') + r'", uni=True)\n        pdf.add_font("DejaVu", "B", r"' + fonte_ok.replace('\\','/') + r'", uni=True)\n        pdf.add_font("DejaVu", "I", r"' + fonte_ok.replace('\\','/') + r'", uni=True)'
        bloco_bf = padrao_fpdf_bf.sub(injecao, bloco_bf, count=1)

    if bloco_bf != bloco_bf_orig:
        main_code = main_code.replace(bloco_bf_orig, bloco_bf)
        print("[OK] BF corrigido.")

# =========================================================
# 2. DFC: substituir "Helvetica" e adicionar add_font
# =========================================================
padrao_dfc = re.compile(
    r'(@app\.get\("/gerar_pdf_analise_dfc/\{id\}"\).*?)(?=\n@app\.|\Z)',
    re.DOTALL
)
match_dfc = padrao_dfc.search(main_code)
if match_dfc:
    bloco_dfc = match_dfc.group(1)
    bloco_dfc_orig = bloco_dfc

    # 2a. Injetar add_font logo após "pdf = FPDF()" — precisa ser antes das chamadas set_font
    padrao_fpdf_dfc = re.compile(r'(pdf\s*=\s*FPDF\([^)]*\))')
    if padrao_fpdf_dfc.search(bloco_dfc):
        injecao = r'\1\n    pdf.add_font("DejaVu", "", r"' + fonte_ok.replace('\\','/') + r'", uni=True)\n    pdf.add_font("DejaVu", "B", r"' + fonte_ok.replace('\\','/') + r'", uni=True)\n    pdf.add_font("DejaVu", "I", r"' + fonte_ok.replace('\\','/') + r'", uni=True)'
        bloco_dfc = padrao_fpdf_dfc.sub(injecao, bloco_dfc, count=1)
        print("[OK] DFC: add_font injetado.")

    # 2b. Substituir "Helvetica" por "DejaVu" APENAS nas chamadas set_font (evita quebrar strings)
    bloco_dfc = bloco_dfc.replace('set_font("Helvetica"', 'set_font("DejaVu"')
    print("[OK] DFC: set_font substituído.")

    if bloco_dfc != bloco_dfc_orig:
        main_code = main_code.replace(bloco_dfc_orig, bloco_dfc)
        print("[OK] DFC corrigido.")

# =========================================================
# 3. Validar sintaxe
# =========================================================
try:
    compile(main_code, arq_main, "exec")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    print("Restaurando backup...")
    shutil.copy2(arq_main + ".bak", arq_main)  # não é usado, por segurança
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] main.py atualizado e validado.")
