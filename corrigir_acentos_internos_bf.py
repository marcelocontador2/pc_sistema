import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_acer_bf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza o bloco da função BF
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
bloco_bf = codigo[idx_bf:fim_bf]
bloco_orig = bloco_bf

# =========================================================
# Substituições de strings SEM ACENTO -> COM ACENTO
# (apenas dentro da função BF)
# =========================================================
substituicoes = [
    # Tabela principal
    ('"Indicador"', '"Indicador"'),  # já ok
    ('"RECEITAS"', '"RECEITAS"'),  # ok
    ('"RECEITAS CORRENTE"', '"RECEITAS CORRENTES"'),  # plural + acento (já era ok)
    ('"Receitas Correntes"', '"Receitas Correntes"'),  # ok
    ('"Receitas de Capital"', '"Receitas de Capital"'),  # ok
    ('"TOTAL DE RECEITAS"', '"TOTAL DE RECEITAS"'),  # ok
    ('"DESPESAS"', '"DESPESAS"'),  # ok
    ('"Despesas Correntes"', '"Despesas Correntes"'),  # ok
    ('"Despesas de Capital"', '"Despesas de Capital"'),  # ok
    ('"TOTAL DE DESPESAS"', '"TOTAL DE DESPESAS"'),  # ok
    ('"EXTRAORCAMENTARIO"', '"EXTRAORÇAMENTÁRIO"'),  # AQUI
    ('"EXTRAORCAMENTÁRIO"', '"EXTRAORÇAMENTÁRIO"'),  # idempotente
    ('"Recebimentos Extraorçamentários"', '"Recebimentos Extraorçamentários"'),  # ok
    ('"Pagamentos Extraorçamentários"', '"Pagamentos Extraorçamentários"'),  # ok
    ('"CAIXA E EQUIVALENTES"', '"CAIXA E EQUIVALENTES"'),  # ok
    ('"Saldo em Espécie do Exercício Anterior"', '"Saldo em Espécie do Exercício Anterior"'),  # ok
    ('"Geração Líquida de Caixa"', '"Geração Líquida de Caixa"'),  # ok
    ('"Saldo em Espécie para o Exercício Seguinte"', '"Saldo em Espécie para o Exercício Seguinte"'),  # ok
    ('"TOTAL GERAL DE INGRESSOS"', '"TOTAL GERAL DE INGRESSOS"'),  # ok
    ('"Receitas Orcamentárias (Corrente + Capital)"', '"Receitas Orçamentárias (Corrente + Capital)"'),  # AQUI
    ('"Recebimentos Extraorçamentários"', '"Recebimentos Extraorçamentários"'),  # ok
    ('"TOTAL DE INGRESSOS"', '"TOTAL DE INGRESSOS"'),  # ok
    ('"TOTAL GERAL DE DISPÊNDIOS"', '"TOTAL GERAL DE DISPÊNDIOS"'),  # AQUI
    ('"TOTAL GERAL DE DISPENDIOS"', '"TOTAL GERAL DE DISPÊNDIOS"'),  # idempotente
    ('"Despesas Orcamentárias (Corrente + Capital)"', '"Despesas Orçamentárias (Corrente + Capital)"'),  # AQUI
    ('"Pagamentos Extraorçamentários"', '"Pagamentos Extraorçamentários"'),  # ok
    ('"TOTAL DE DISPÊNDIOS"', '"TOTAL DE DISPÊNDIOS"'),  # AQUI
    ('"TOTAL DE DISPENDIOS"', '"TOTAL DE DISPÊNDIOS"'),  # idempotente
    ('"Período Atual"', '"Período Atual"'),  # ok
    ('"Período Anterior"', '"Período Anterior"'),  # ok
    ('"Balanço Financeiro"', '"Balanço Financeiro"'),  # ok (já foi feito)
    ('"Período: {periodo}"', '"Período: {periodo}"'),  # ok
    # Rodapé
    ('"Cofen • Análise das Demonstrações Contábeis"', '"Cofen • Análise das Demonstrações Contábeis"'),  # ok
    ('"Gerado em:"', '"Gerado em:"'),  # ok
]

# Aplicar as substituições
for velho, novo in substituicoes:
    if velho != novo:
        bloco_bf = bloco_bf.replace(velho, novo)
        print(f"[OK] '{velho}' → '{novo}'")

# =========================================================
# Substituição extra: caso o texto esteja em variável (não em string literal)
# =========================================================
# Procura por f-strings ou variáveis que possam ter "EXTRAORCAMENTARIO", "Orcamentária", etc.
# Sem acento nas variáveis
bloco_bf = bloco_bf.replace("EXTRAORCAMENTARIO", "EXTRAORÇAMENTÁRIO")
bloco_bf = bloco_bf.replace("Orcamentárias", "Orçamentárias")
bloco_bf = bloco_bf.replace("Orcamentaria", "Orçamentária")
bloco_bf = bloco_bf.replace("Orcamentário", "Orçamentário")
bloco_bf = bloco_bf.replace("DISPENDIOS", "DISPÊNDIOS")
bloco_bf = bloco_bf.replace("Dispensdios", "Dispêndios")
bloco_bf = bloco_bf.replace("ESPECIE", "ESPÉCIE")
bloco_bf = bloco_bf.replace("Especie", "Espécie")
bloco_bf = bloco_bf.replace("Exercicio", "Exercício")
bloco_bf = bloco_bf.replace("exercicio", "exercício")
bloco_bf = bloco_bf.replace("Geracao", "Geração")
bloco_bf = bloco_bf.replace("geracao", "geração")
bloco_bf = bloco_bf.replace("Liquida", "Líquida")
bloco_bf = bloco_bf.replace("liquida", "líquida")

# =========================================================
# Aplicar mudanças
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
print("[OK] main.py salvo com acentos internos do BF corrigidos.")
