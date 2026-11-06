import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_cabecalho_dfc_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza o bloco da função DFC
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
bloco_dfc = codigo[idx_dfc:fim_dfc]
bloco_orig = bloco_dfc

# =========================================================
# Correções do CABEÇALHO e LINHAS DE REFERÊNCIA
# =========================================================
substituicoes = [
    # Cabeçalho principal (linha 2081)
    ('"COFEN/BR - ANALISE DA DEMONSTRACAO DO FLUXO DE CAIXA"', 
     '"COFEN/BR - ANÁLISE DA DEMONSTRAÇÃO DO FLUXO DE CAIXA"'),
    
    # Linhas de referência (linhas 2086-2087)
    ('f"Periodo de Referencia: {periodo.replace(\'-\', \' \')}"', 
     'f"Período de Referência: {periodo.replace(\'-\', \' \')}"'),
    ('f"Data de Geracao do Relatorio: {data_geracao}"', 
     'f"Data de Geração do Relatório: {data_geracao}"'),
]

for velho, novo in substituicoes:
    if velho in bloco_dfc:
        bloco_dfc = bloco_dfc.replace(velho, novo)
        print(f"[OK] Substituído: {velho[:60]}...")

# =========================================================
# Remove add_font duplicado (mantém apenas 1 conjunto)
# =========================================================
add_fonts_original = '''    pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)'''

add_fonts_novo = '''    pdf.add_font("ArialUnicode", "", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "B", r"C:/Windows/Fonts/arial.ttf", uni=True)
    pdf.add_font("ArialUnicode", "I", r"C:/Windows/Fonts/arial.ttf", uni=True)'''

if add_fonts_original in bloco_dfc:
    bloco_dfc = bloco_dfc.replace(add_fonts_original, add_fonts_novo)
    print("[OK] add_font duplicado removido.")

# =========================================================
# Aplicar mudanças
# =========================================================
codigo = codigo.replace(bloco_orig, bloco_dfc)

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo.")
