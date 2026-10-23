import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}

def buscar_valor(cursor, grupo):
    cursor.execute("SELECT valor_atual FROM demonstracao_resumo WHERE grupo_demonstrativo = %s ORDER BY id DESC LIMIT 1;", (grupo,))
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0

def analisar_completo():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # === DADOS DO BP ===
    ativo_circulante = buscar_valor(cursor, "Ativo Circulante")
    ativo_nao_circulante = buscar_valor(cursor, "Ativo Nao Circulante")
    passivo_circulante = buscar_valor(cursor, "Passivo Circulante")
    passivo_nao_circulante = buscar_valor(cursor, "Passivo Nao Circulante")
    patrimonio_liquido = buscar_valor(cursor, "Patrimonio Liquido")

    # === DADOS DO BO ===
    receita_realizada = buscar_valor(cursor, "Receita Realizada")
    despesa_empenhada = buscar_valor(cursor, "Despesa Empenhada")

    # === DADOS DO BF ===
    receita_orcamentaria = buscar_valor(cursor, "Receita Orcamentaria")
    despesa_orcamentaria = buscar_valor(cursor, "Despesa Orcamentaria")
    saldo_inicial = buscar_valor(cursor, "Saldo Inicial")
    saldo_final = buscar_valor(cursor, "Saldo Final")

    # === DADOS DA DFC ===
    caixa_inicial = buscar_valor(cursor, "Caixa Inicial")
    caixa_final = buscar_valor(cursor, "Caixa Final")

    # === DADOS DA DVP ===
    variacoes_ativas = buscar_valor(cursor, "Variacoes Ativas")
    variacoes_diminutivas = buscar_valor(cursor, "Variacoes Diminutivas")
    superavit_patrimonial = buscar_valor(cursor, "Superavit Patrimonial")

    # === DADOS DO DMPL ===
    pl_inicial = buscar_valor(cursor, "PL Inicial")
    resultado_periodo = buscar_valor(cursor, "Resultado Periodo")
    pl_final = buscar_valor(cursor, "PL Final")

    # === CÁLCULOS ===
    ativo_total = ativo_circulante + ativo_nao_circulante
    passivo_total = passivo_circulante + passivo_nao_circulante
    superavit_orcamentario = receita_realizada - despesa_empenhada

    liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante else 0
    liquidez_geral = (ativo_circulante + ativo_nao_circulante) / (passivo_circulante + passivo_nao_circulante) if (passivo_circulante + passivo_nao_circulante) else 0
    endividamento_geral = (passivo_total / ativo_total) * 100 if ativo_total else 0
    margem_patrimonial = (superavit_patrimonial / variacoes_ativas) * 100 if variacoes_ativas else 0

    # === EXIBIÇÃO ===
    print("\n" + "="*70)
    print("📊 RELATÓRIO DE ANÁLISE CONTÁBIL — COFEN")
    print("Período: Jan-Set/2026 (Acumulado)")
    print("="*70)

    print("\n🏛️  RESULTADOS GERAIS (Páginas 4 e 5)")
    print("-"*50)
    print(f"Ativo Total:............ R$ {ativo_total:,.2f}")
    print(f"Passivo Total:.......... R$ {passivo_total:,.2f}")
    print(f"Patrimônio Líquido:..... R$ {patrimonio_liquido:,.2f}")
    print(f"Superávit Orçamentário:. R$ {superavit_orcamentario:,.2f}")
    print(f"Superávit Patrimonial:.. R$ {superavit_patrimonial:,.2f}")

    print("\n📈  ANÁLISE ECONÔMICO-FINANCEIRA (Páginas 7 e 8)")
    print("-"*50)
    print(f"Liquidez Corrente:...... {liquidez_corrente:.2f}")
    print(f"Liquidez Geral:......... {liquidez_geral:.2f}")
    print(f"Endividamento Geral:.... {endividamento_geral:.2f}%")

    print("\n💰  EXECUÇÃO ORÇAMENTÁRIA (Páginas 9 e 10)")
    print("-"*50)
    print(f"Receita Realizada:...... R$ {receita_realizada:,.2f}")
    print(f"Despesa Empenhada:...... R$ {despesa_empenhada:,.2f}")
    print(f"Superávit Orçamentário:. R$ {superavit_orcamentario:,.2f}")
    print(f"Taxa de Execução:....... {(receita_realizada / receita_orcamentaria) * 100 if receita_orcamentaria else 0:.2f}%")

    print("\n💵  BALANÇO FINANCEIRO (Página 11)")
    print("-"*50)
    print(f"Saldo Inicial:.......... R$ {saldo_inicial:,.2f}")
    print(f"Receita Orçamentária:... R$ {receita_orcamentaria:,.2f}")
    print(f"Despesa Orçamentária:... R$ {despesa_orcamentaria:,.2f}")
    print(f"Saldo Final:............ R$ {saldo_final:,.2f}")
    print(f"Variação do Saldo:...... R$ {saldo_final - saldo_inicial:,.2f}")

    print("\n📊  VARIAÇÕES PATRIMONIAIS (Página 12)")
    print("-"*50)
    print(f"Variações Ativas:....... R$ {variacoes_ativas:,.2f}")
    print(f"Variações Diminutivas:.. R$ {variacoes_diminutivas:,.2f}")
    print(f"Superávit Patrimonial:.. R$ {superavit_patrimonial:,.2f}")
    print(f"Margem Patrimonial:..... {margem_patrimonial:.2f}%")

    print("\n📋  DEMONSTRAÇÃO DAS MUTAÇÕES DO PL (DMPL)")
    print("-"*50)
    print(f"PL Inicial:............. R$ {pl_inicial:,.2f}")
    print(f"Resultado do Período:... R$ {resultado_periodo:,.2f}")
    print(f"PL Final:............... R$ {pl_final:,.2f}")

    print("\n" + "="*70)
    print("✅  EQUAÇÃO PATRIMONIAL: Ativo = Passivo + PL")
    print(f"    {ativo_total:,.2f} = {passivo_total + patrimonio_liquido:,.2f}")
    print(f"    Diferença: {abs(ativo_total - (passivo_total + patrimonio_liquido)):,.2f}")
    print("="*70)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    analisar_completo()