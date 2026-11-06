import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_arial_unicode_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Fonte TTF
fonte_ok = "C:/Windows/Fonts/arial.ttf"
if not os.path.exists(fonte_ok):
    print("[ERRO] arial.ttf não encontrado.")
    exit()

# =========================================================
# 1. Corrigir a definição de fonte_padrao do BF (linha 1712)
# =========================================================
for i in range(1700, 1720):  # busca próxima à linha 1712
    if 'fonte_padrao = "Helvetica"' in linhas[i]:
        linhas[i] = linhas[i].replace('fonte_padrao = "Helvetica"', 'fonte_padrao = "ArialUnicode"')
        print(f"[OK] Linha {i+1}: fonte_padrao do BF trocada para ArialUnicode.")
        break

# =========================================================
# 2. Encontrar o pdf = FPDF() do BF e injetar add_font após
# =========================================================
# Localiza o bloco da função BF
bf_start = None
for i in range(1680, 1730):
    if "def gerar_pdf_analise_financeira_bf" in linhas[i]:
        bf_start = i
        break

if bf_start:
    # Procura pdf = FPDF() a partir de bf_start
    for j in range(bf_start, bf_start + 100):
        if "pdf = FPDF()" in linhas[j] or "pdf=FPDF()" in linhas[j]:
            # Injeta add_font logo após
            injecao = f'        pdf.add_font("ArialUnicode", "", r"{fonte_ok}", uni=True)\n        pdf.add_font("ArialUnicode", "B", r"{fonte_ok}", uni=True)\n        pdf.add_font("ArialUnicode", "I", r"{fonte_ok}", uni=True)\n'
            linhas.insert(j + 1, injecao)
            print(f"[OK] BF: add_font(ArialUnicode) injetado após linha {j+1}.")
            break

# =========================================================
# 3. Corrigir as chamadas set_font("Helvetica", ...) do DFC
#    (linhas 2071-2184)
# =========================================================
for i in range(2060, 2200):
    if 'set_font("Helvetica"' in linhas[i]:
        linhas[i] = linhas[i].replace('set_font("Helvetica"', 'set_font("ArialUnicode"')
print("[OK] DFC: set_font('Helvetica') trocado por set_font('ArialUnicode') nas linhas 2071-2184.")

# =========================================================
# 4. Encontrar o pdf = FPDF() do DFC e injetar add_font após
# =========================================================
dfc_start = None
for i in range(2040, 2080):
    if "def gerar_pdf_analise_dfc" in linhas[i]:
        dfc_start = i
        break

if dfc_start:
    for j in range(dfc_start, dfc_start + 50):
        if "pdf = FPDF(" in linhas[j] or "pdf=FPDF(" in linhas[j]:
            injecao = f'    pdf.add_font("ArialUnicode", "", r"{fonte_ok}", uni=True)\n    pdf.add_font("ArialUnicode", "B", r"{fonte_ok}", uni=True)\n    pdf.add_font("ArialUnicode", "I", r"{fonte_ok}", uni=True)\n'
            linhas.insert(j + 1, injecao)
            print(f"[OK] DFC: add_font(ArialUnicode) injetado após linha {j+1}.")
            break

# =========================================================
# 5. Validar sintaxe e salvar
# =========================================================
novo_codigo = "".join(linhas)
try:
    compile(novo_codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    print("main.py NÃO foi alterado.")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(novo_codigo)
print("[OK] main.py salvo com sucesso.")
print("[INFO] Agora reinicie o servidor e gere os PDFs do BF e DFC.")
