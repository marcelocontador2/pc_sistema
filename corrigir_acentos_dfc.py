import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_acer_dfc_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza o bloco da função DFC
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
bloco_dfc = codigo[idx_dfc:fim_dfc]
bloco_orig = bloco_dfc

# =========================================================
# Substituições de strings SEM ACENTO -> COM ACENTO
# (apenas dentro da função DFC)
# =========================================================
substituicoes = [
    # Cabeçalhos da tabela
    ('"ESPECIFICACAO"', '"ESPECIFICAÇÃO"'),
    ('"PERIODO ATUAL"', '"PERÍODO ATUAL"'),
    ('"PERIODO ANTERIOR"', '"PERÍODO ANTERIOR"'),
    ('"VAR. (%)"', '"VAR. (%)"'),  # já ok

    # Seções principais
    ('"FLUXO DE CAIXA DAS ATIVIDADES DAS OPERACOES"', '"FLUXO DE CAIXA DAS ATIVIDADES DAS OPERAÇÕES"'),
    ('"FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO"', '"FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO"'),  # ok
    ('"FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO"', '"FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO"'),  # ok
    ('"APURACAO DO FLUXO DE CAIXA DO PERIODO"', '"APURAÇÃO DO FLUXO DE CAIXA DO PERÍODO"'),

    # Linhas da tabela
    ('"Ingressos Operacionais"', '"Ingressos Operacionais"'),  # ok
    ('"Desembolsos Operacionais"', '"Desembolsos Operacionais"'),  # ok
    ('"Caixa Liquido das Operacoes"', '"Caixa Líquido das Operações"'),
    ('"Ingressos de Investimento"', '"Ingressos de Investimento"'),  # ok
    ('"Desembolsos de Investimento"', '"Desembolsos de Investimento"'),  # ok
    ('"Caixa Liquido de Investimento"', '"Caixa Líquido de Investimento"'),
    ('"Ingressos de Financiamento"', '"Ingressos de Financiamento"'),  # ok
    ('"Desembolsos de Financiamento"', '"Desembolsos de Financiamento"'),  # ok
    ('"Caixa Liquido de Financiamento"', '"Caixa Líquido de Financiamento"'),
    ('"Geracao Liquida de Caixa"', '"Geração Líquida de Caixa"'),
    ('"Caixa e Equivalentes Inicial"', '"Caixa e Equivalentes Inicial"'),  # ok
    ('"Caixa e Equivalentes Final"', '"Caixa e Equivalentes Final"'),  # ok

    # Análises textuais
    ('"1. ANALISE DAS ATIVIDADES OPERACIONAIS"', '"1. ANÁLISE DAS ATIVIDADES OPERACIONAIS"'),
    ('"2. ANALISE DAS ATIVIDADES DE INVESTIMENTO"', '"2. ANÁLISE DAS ATIVIDADES DE INVESTIMENTO"'),
    ('"3. ANALISE DAS ATIVIDADES DE FINANCIAMENTO"', '"3. ANÁLISE DAS ATIVIDADES DE FINANCIAMENTO"'),
    ('"4. CONCLUSAO SOBRE A LIQUIDEZ"', '"4. CONCLUSÃO SOBRE A LIQUIDEZ"'),
]

# Aplicar as substituições de texto
for velho, novo in substituicoes:
    if velho != novo and velho in bloco_dfc:
        bloco_dfc = bloco_dfc.replace(velho, novo)
        print(f"[OK] '{velho}' → '{novo}'")

# =========================================================
# Substituições de textos dentro de f-strings e strings soltas
# =========================================================
# Textos que estão dentro de variáveis ou parágrafos longos
textos_livres = [
    ("As atividades operacionais geraram um caixa liquido positivo de R$", 
     "As atividades operacionais geraram um caixa líquido positivo de R$"),
    ("As atividades operacionais apresentaram um caixa liquido negativo de R$", 
     "As atividades operacionais apresentaram um caixa líquido negativo de R$"),
    ("no periodo atual", "no período atual"),
    ("o que e comum e esperado quando a entidade realiza aquisiçoes de ativos (investimentos) e imobilizaçoes.", 
     "o que é comum e esperado quando a entidade realiza aquisições de ativos (investimentos) e imobilizações."),
    ("Nao houve movimentacao significativa no fluxo de caixa de financiamentos no periodo.", 
     "Não houve movimentação significativa no fluxo de caixa de financiamentos no período."),
    ("A entidade encerrou o periodo com um saldo de caixa de R$", 
     "A entidade encerrou o período com um saldo de caixa de R$"),
    ("(variaçao de R$", "(variação de R$"),
    ("em relacao ao saldo inicial de R$", "em relação ao saldo inicial de R$"),
    ("O aumento no saldo de caixa demonstra uma boa geracao de recursos no periodo.", 
     "O aumento no saldo de caixa demonstra uma boa geração de recursos no período."),
    ("A reducao no saldo de caixa requer atencao aos proximos periodos para garantir a manutencao das atividades.", 
     "A redução no saldo de caixa requer atenção aos próximos períodos para garantir a manutenção das atividades."),
    ("O fluxo de caixa de investimentos foi negativo em R$", 
     "O fluxo de caixa de investimentos foi negativo em R$"),
    ("O fluxo de caixa de investimentos foi positivo em R$", 
     "O fluxo de caixa de investimentos foi positivo em R$"),
    ("indicando que a entidade obteve mais recursos com alienacao de ativos do que gastou com aquisicoes.", 
     "indicando que a entidade obteve mais recursos com alienação de ativos do que gastou com aquisições."),
    ("O fluxo de caixa de financiamentos foi positivo em R$", 
     "O fluxo de caixa de financiamentos foi positivo em R$"),
    ("decorrente de captacao de emprestimos ou financiamentos.", 
     "decorrente de captação de empréstimos ou financiamentos."),
    ("O fluxo de caixa de financiamentos foi negativo em R$", 
     "O fluxo de caixa de financiamentos foi negativo em R$"),
    ("indicando amortizacao de dividas ou devolucao de recursos.", 
     "indicando amortização de dívidas ou devolução de recursos."),
]

for velho, novo in textos_livres:
    if velho in bloco_dfc:
        bloco_dfc = bloco_dfc.replace(velho, novo)
        print(f"[OK] Texto livre corrigido.")

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
print("[OK] main.py salvo com acentos do DFC corrigidos.")
