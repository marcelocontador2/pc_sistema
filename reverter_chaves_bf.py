import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fix_chaves_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza o bloco da função BF
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
bloco_bf = codigo[idx_bf:fim_bf]
bloco_orig = bloco_bf

# =========================================================
# 1. Reverter chaves de dicionário que foram acidentalmente acentuadas
# =========================================================
# As chaves internas do dicionário `d` NÃO devem ter acento
substituicoes_reverter = [
    ('["geração_líquida"]', '["geracao_liquida"]'),
    ('["geração"]', '["geracao"]'),
    ('["geração_liquida"]', '["geracao_liquida"]'),
    ('["exercício_anterior"]', '["exercicio_anterior"]'),
    ('["exercício_seguinte"]', '["exercicio_seguinte"]'),
    ('["saldo_anterior"]', '["saldo_anterior"]'),
]

for velho, novo in substituicoes_reverter:
    if velho in bloco_bf:
        bloco_bf = bloco_bf.replace(velho, novo)
        print(f"[REVERTIDO] Chave: {velho} → {novo}")

# =========================================================
# 2. Aplicar acentos APENAS nos textos que vão pro PDF
# =========================================================
# Substituições de strings (só textos visíveis, não chaves)
substituicoes_textos = [
    ('"TOTAL DE DISPENDIOS"', '"TOTAL DE DISPÊNDIOS"'),
    ('"TOTAL GERAL DE DISPENDIOS"', '"TOTAL GERAL DE DISPÊNDIOS"'),
    ('"Receitas Orcamentarias (Corrente + Capital)"', '"Receitas Orçamentárias (Corrente + Capital)"'),
    ('"Despesas Orcamentarias (Corrente + Capital)"', '"Despesas Orçamentárias (Corrente + Capital)"'),
]

for velho, novo in substituicoes_textos:
    if velho in bloco_bf:
        bloco_bf = bloco_bf.replace(velho, novo)
        print(f"[OK] Texto: {velho} → {novo}")

# =========================================================
# 3. Validar e salvar
# =========================================================
codigo = codigo.replace(bloco_orig, bloco_bf)

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo.")
