import psycopg2
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}
def buscar_valor(cursor, grupo, periodo_id):
    cursor.execute(
        "SELECT valor_atual FROM demonstracao_resumo "
        "WHERE grupo_demonstrativo = %s AND periodo_id = %s "
        "ORDER BY id DESC LIMIT 1;",
        (grupo, periodo_id)
    )
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0


def get_periodo_id(cursor, ano):
    cursor.execute(
        "SELECT id FROM periodo WHERE ano = %s AND periodo_acumulado = %s;",
        (ano, "Jan-Set")
    )
    res = cursor.fetchone()
    return res[0] if res else None
def analisar_resultados():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    pid_2026 = get_periodo_id(cursor, 2026)
    if not pid_2026:
        print("ERRO: periodo 2026 nao encontrado")
        cursor.close(); conn.close()
        return
    # Dados do BP
    ativo_circulante = buscar_valor(cursor, "Ativo Circulante", pid_2026)
    ativo_nao_circulante = buscar_valor(cursor, "Ativo Nao Circulante", pid_2026)
    passivo_circulante = buscar_valor(cursor, "Passivo Circulante", pid_2026)
    passivo_nao_circulante = buscar_valor(cursor, "Passivo Nao Circulante", pid_2026)
    patrimonio_liquido = buscar_valor(cursor, "Patrimonio Liquido", pid_2026)
    # Dados do BO
    receita_realizada = buscar_valor(cursor, "Receita Realizada", pid_2026)
    despesa_empenhada = buscar_valor(cursor, "Despesa Empenhada", pid_2026)
    # Cálculos
    ativo_total = ativo_circulante + ativo_nao_circulante
    passivo_total = passivo_circulante + passivo_nao_circulante
    superavit_orcamentario = receita_realizada - despesa_empenhada
    # Índices
    liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante else 0
    endividamento_geral = (passivo_total / ativo_total) * 100 if ativo_total else 0
    print("\n" + "="*60)
    print("📊 RESULTADOS GERAIS — ANÁLISE CONSOLIDADA")
    print("="*60)
    print(f"Ativo Total:............ R$ {ativo_total:,.2f}")
    print(f"Passivo Total:.......... R$ {passivo_total:,.2f}")
    print(f"Patrimônio Líquido:..... R$ {patrimonio_liquido:,.2f}")
    print(f"Receita Realizada:...... R$ {receita_realizada:,.2f}")
    print(f"Despesa Empenhada:...... R$ {despesa_empenhada:,.2f}")
    print(f"Superávit Orçamentário:. R$ {superavit_orcamentario:,.2f}")
    print("="*60)
    print("\n📈 ÍNDICES ECONÔMICO-FINANCEIROS")
    print("-"*50)
    print(f"Liquidez Corrente:...... {liquidez_corrente:.2f}")
    print(f"Endividamento Geral:.... {endividamento_geral:.2f}%")
    print("="*60)
    # Validação
    diferenca = abs(ativo_total - (passivo_total + patrimonio_liquido))
    if diferenca < 0.01:
        print("✅ EQUAÇÃO PATRIMONIAL: Ativo = Passivo + PL (Consistente)")
    else:
        print(f"⚠️ ALERTA: Equação patrimonial não fecha! Diferença: R$ {diferenca:,.2f}")
    print("="*60)
    cursor.close()
    conn.close()
if __name__ == "__main__":
    analisar_resultados()
