import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_correcao_acer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

fonte = "C:/Windows/Fonts/arial.ttf"

# =========================================================
# 1. DFC: Injetar add_font após pdf = FPDF(...)
# =========================================================
# Localizar o bloco da função DFC
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
bloco_dfc = codigo[idx_dfc:fim_dfc]

# Localizar a linha pdf = FPDF(...)
padrao_fpdf = re.compile(r'(pdf\s*=\s*FPDF\([^)]*\))')
if padrao_fpdf.search(bloco_dfc):
    injecao = r'\1\n    pdf.add_font("ArialUnicode", "", r"' + fonte + r'", uni=True)\n    pdf.add_font("ArialUnicode", "B", r"' + fonte + r'", uni=True)\n    pdf.add_font("ArialUnicode", "I", r"' + fonte + r'", uni=True)'
    bloco_dfc = padrao_fpdf.sub(injecao, bloco_dfc, count=1)
    print("[OK] DFC: add_font injetado após pdf = FPDF(...).")
else:
    print("[AVISO] DFC: pdf = FPDF(...) não encontrado.")

# Substituir o bloco DFC no código
codigo = codigo[:idx_dfc] + bloco_dfc + codigo[fim_dfc:]

# =========================================================
# 2. BF: Adicionar acentos nas strings
# =========================================================
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
bloco_bf = codigo[idx_bf:fim_bf]

# Substituições:
substituicoes = [
    ('"Balanco Financeiro"', '"Balanço Financeiro"'),
    ('"Periodo: {periodo}"', '"Período: {periodo}"'),
    ('"TOTAL DE RECEITAS"', '"TOTAL DE RECEITAS"'),  # já está ok
    ('"RECEITAS"', '"RECEITAS"'),  # ok
    ('"DESPESAS"', '"DESPESAS"'),  # ok
    ('"Saldo p/ Exerc. Seguinte"', '"Saldo p/ Exerc. Seguinte"'),  # ok
    ('"Período Atual"', '"Período Atual"'),  # ok
    ('"Período Anterior"', '"Período Anterior"'),  # ok
]
for velho, novo in substituicoes:
    bloco_bf = bloco_bf.replace(velho, novo)

# Mais substituições específicas dentro do BF
bloco_bf = bloco_bf.replace('"Total de Receitas"', '"Total de Receitas"')  # já ok
bloco_bf = bloco_bf.replace('"Total de Despesas"', '"Total de Despesas"')  # já ok
bloco_bf = bloco_bf.replace('"Balanco"', '"Balanço"')
bloco_bf = bloco_bf.replace('"Periodo"', '"Período"')

# Substituir o bloco BF no código
codigo = codigo[:idx_bf] + bloco_bf + codigo[fim_bf:]

# =========================================================
# 3. Validar sintaxe e salvar
# =========================================================
try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo com sucesso.")
print("[INFO] DFC: add_font injetado. BF: acentos corrigidos.")
