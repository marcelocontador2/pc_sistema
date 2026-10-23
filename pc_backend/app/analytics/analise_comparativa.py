import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}

def buscar_valor(cursor, grupo, ano):
    cursor.execute("""
        SELECT d.valor_atual FROM demonstracao_resumo d
        JOIN periodo p ON d.periodo_id = p.id
        WHERE d.grupo_demonstrativo = %s AND p.ano = %s AND p.periodo_acumulado = 'Jan-Set'
        ORDER BY d.id DESC LIMIT 1;
    """, (grupo, ano))
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0

def calcular_variacao(valor_atual, valor_anterior):
    if valor_anterior == 0:
        return 0.0
    return ((valor_atual - valor_anterior) / valor_anterior) * 100

def analisar_comparativo():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # === DADOS 2026 ===
    ativo_circulante_2026 = buscar_valor(cursor, "Ativo Circulante", 2026)
    ativo_nao_circulante_2026 = buscar_valor(cursor, "Ativo Nao Circulante", 2026)
    passivo_circulante_2026 = buscar_valor(cursor, "Passivo Circulante", 2026)
    passivo_nao_circulante_2026 = buscar_valor(cursor, "Passivo Nao Circulante", 2026)
    patrimonio_liquido_2026 = buscar_valor(cursor, "Patrimonio Liquido", 2026)
    receita_realizada_2026 = buscar_valor(cursor, "Receita Realizada", 2026)
    despesa_empenhada_2026 = buscar_valor(cursor, "Despesa Empenhada", 2026)
    superavit_patrimonial_2026 = buscar_valor(cursor, "Superavit Patrimonial", 2026)
    variacoes_ativas_2026 = buscar_valor(cursor, "Variacoes Ativas", 2026)
    variacoes_diminutivas_2026 = buscar_valor(cursor, "Variacoes Diminutivas", 2026)
    caixa_inicial_2026 = buscar_valor(cursor, "Caixa Inicial", 2026)
    caixa_final_2026 = buscar_valor(cursor, "Caixa Final", 2026)

    # === DADOS 2025 ===
    ativo_circulante_2025 = buscar_valor(cursor, "Ativo Circulante", 2025)
    ativo_nao_circulante_2025 = buscar_valor(cursor, "Ativo Nao Circulante", 2025)
    passivo_circulante_2025 = buscar_valor(cursor, "Passivo Circulante", 2025)
    passivo_nao_circulante_2025 = buscar_valor(cursor, "Passivo Nao Circulante", 2025)
    patrimonio_liquido_2025 = buscar_valor(cursor, "Patrimonio Liquido", 2025)
    receita_realizada_2025 = buscar_valor(cursor, "Receita Realizada", 2025)
    despesa_empenhada_2025 = buscar_valor(cursor, "Despesa Empenhada", 2025)
    superavit_patrimonial_2025 = buscar_valor(cursor, "Superavit Patrimonial", 2025)
    variacoes_ativas_2025 = buscar_valor(cursor, "Variacoes Ativas", 2025)
    variacoes_diminutivas_2025 = buscar_valor(cursor, "Variacoes Diminutivas", 2025)
    caixa_inicial_2025 = buscar_valor(cursor, "Caixa Inicial", 2025)
    caixa_final_2025 = buscar_valor(cursor, "Caixa Final", 2025)

    # === CÁLCULOS DE TOTAIS ===
    ativo_total_2026 = ativo_circulante_2026 + ativo_nao_circulante_2026
    ativo_total_2025 = ativo_circulante_2025 + ativo_nao_circulante_2025
    passivo_total_2026 = passivo_circulante_2026 + passivo_nao_circulante_2026
    passivo_total_2025 = passivo_circulante_2025 + passivo_nao_circulante_2025
    superavit_orcamentario_2026 = receita_realizada_2026 - despesa_empenhada_2026
    superavit_orcamentario_2025 = receita_realizada_2025 - despesa_empenhada_2025

    # === VARIAÇÕES PERCENTUAIS ===
    var_ac = calcular_variacao(ativo_circulante_2026, ativo_circulante_2025)
    var_anc = calcular_variacao(ativo_nao_circulante_2026, ativo_nao_circulante_2025)
    var_at = calcular_variacao(ativo_total_2026, ativo_total_2025)
    var_pc = calcular_variacao(passivo_circulante_2026, passivo_circulante_2025)
    var_pnc = calcular_variacao(passivo_nao_circulante_2026, passivo_nao_circulante_2025)
    var_pl = calcular_variacao(patrimonio_liquido_2026, patrimonio_liquido_2025)
    var_rr = calcular_variacao(receita_realizada_2026, receita_realizada_2025)
    var_de = calcular_variacao(despesa_empenhada_2026, despesa_empenhada_2025)
    var_so = calcular_variacao(superavit_orcamentario_2026, superavit_orcamentario_2025)
    var_sp = calcular_variacao(superavit_patrimonial_2026, superavit_patrimonial_2025)

    # === ÍNDICES ===
    liquidez_corrente = ativo_circulante_2026 / passivo_circulante_2026 if passivo_circulante_2026 else 0
    liquidez_geral = (ativo_circulante_2026 + ativo_nao_circulante_2026) / (passivo_circulante_2026 + passivo_nao_circulante_2026) if (passivo_circulante_2026 + passivo_nao_circulante_2026) else 0
    endividamento_geral = (passivo_total_2026 / ativo_total_2026) * 100 if ativo_total_2026 else 0
    margem_patrimonial = (superavit_patrimonial_2026 / variacoes_ativas_2026) * 100 if variacoes_ativas_2026 else 0

    # === EXIBIÇÃO ===
    print("\n" + "="*70)
    print("📊 ANÁLISE COMPARATIVA — 2025 vs 2026 (Jan-Set)")
    print("="*70)

    print("\n🏛️  BALANÇO PATRIMONIAL (Páginas 7 e 8)")
    print("-"*50)
    print(f"{'Conta':<30} {'2025 (R$)':>15} {'2026 (R$)':>15} {'Var. (%)':>10}")
    print("-"*70)
    print(f"{'Ativo Circulante':<30} {ativo_circulante_2025:>15,.2f} {ativo_circulante_2026:>15,.2f} {var_ac:>9.2f}%")
    print(f"{'Ativo Não Circulante':<30} {ativo_nao_circulante_2025:>15,.2f} {ativo_nao_circulante_2026:>15,.2f} {var_anc:>9.2f}%")
    print(f"{'Ativo Total':<30} {ativo_total_2025:>15,.2f} {ativo_total_2026:>15,.2f} {var_at:>9.2f}%")
    print(f"{'Passivo Circulante':<30} {passivo_circulante_2025:>15,.2f} {passivo_circulante_2026:>15,.2f} {var_pc:>9.2f}%")
    print(f"{'Passivo Não Circulante':<30} {passivo_nao_circulante_2025:>15,.2f} {passivo_nao_circulante_2026:>15,.2f} {var_pnc:>9.2f}%")
    print(f"{'Patrimônio Líquido':<30} {patrimonio_liquido_2025:>15,.2f} {patrimonio_liquido_2026:>15,.2f} {var_pl:>9.2f}%")

    print("\n💰  EXECUÇÃO ORÇAMENTÁRIA (Páginas 9 e 10)")
    print("-"*50)
    print(f"{'Indicador':<30} {'2025 (R$)':>15} {'2026 (R$)':>15} {'Var. (%)':>10}")
    print("-"*70)
    print(f"{'Receita Realizada':<30} {receita_realizada_2025:>15,.2f} {receita_realizada_2026:>15,.2f} {var_rr:>9.2f}%")
    print(f"{'Despesa Empenhada':<30} {despesa_empenhada_2025:>15,.2f} {despesa_empenhada_2026:>15,.2f} {var_de:>9.2f}%")
    print(f"{'Superávit Orçamentário':<30} {superavit_orcamentario_2025:>15,.2f} {superavit_orcamentario_2026:>15,.2f} {var_so:>9.2f}%")

    print("\n📊  VARIAÇÕES PATRIMONIAIS (Página 12)")
    print("-"*50)
    print(f"{'Indicador':<30} {'2025 (R$)':>15} {'2026 (R$)':>15} {'Var. (%)':>10}")
    print("-"*70)
    print(f"{'Variações Ativas':<30} {variacoes_ativas_2025:>15,.2f} {variacoes_ativas_2026:>15,.2f} {calcular_variacao(variacoes_ativas_2026, variacoes_ativas_2025):>9.2f}%")
    print(f"{'Variações Diminutivas':<30} {variacoes_diminutivas_2025:>15,.2f} {variacoes_diminutivas_2026:>15,.2f} {calcular_variacao(variacoes_diminutivas_2026, variacoes_diminutivas_2025):>9.2f}%")
    print(f"{'Superávit Patrimonial':<30} {superavit_patrimonial_2025:>15,.2f} {superavit_patrimonial_2026:>15,.2f} {var_sp:>9.2f}%")
    print(f"{'Margem Patrimonial':<30} {'':>15} {margem_patrimonial:>15.2f}% {'':>10}")

    print("\n📈  ÍNDICES ECONÔMICO-FINANCEIROS (2026)")
    print("-"*50)
    print(f"Liquidez Corrente:...... {liquidez_corrente:.2f}")
    print(f"Liquidez Geral:......... {liquidez_geral:.2f}")
    print(f"Endividamento Geral:.... {endividamento_geral:.2f}%")
    print(f"Margem Patrimonial:..... {margem_patrimonial:.2f}%")

    print("\n💵  BALANÇO FINANCEIRO (Página 11)")
    print("-"*50)
    print(f"{'Indicador':<30} {'2025 (R$)':>15} {'2026 (R$)':>15}")
    print("-"*70)
    print(f"{'Caixa Inicial':<30} {caixa_inicial_2025:>15,.2f} {caixa_inicial_2026:>15,.2f}")
    print(f"{'Caixa Final':<30} {caixa_final_2025:>15,.2f} {caixa_final_2026:>15,.2f}")

    print("\n" + "="*70)
    print("✅  EQUAÇÃO PATRIMONIAL (2026)")
    print(f"    {ativo_total_2026:,.2f} = {passivo_total_2026 + patrimonio_liquido_2026:,.2f}")
    print(f"    Diferença: {abs(ativo_total_2026 - (passivo_total_2026 + patrimonio_liquido_2026)):,.2f}")
    print("="*70)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    analisar_comparativo()