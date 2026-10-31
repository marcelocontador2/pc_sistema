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
def analisar_bp():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # --- Dados 2026 ---
    ativo_circulante = buscar_valor(cursor, "Ativo Circulante")
    ativo_nao_circulante = buscar_valor(cursor, "Ativo Nao Circulante")
    passivo_circulante = buscar_valor(cursor, "Passivo Circulante")
    passivo_nao_circulante = buscar_valor(cursor, "Passivo Nao Circulante")
    patrimonio_liquido = buscar_valor(cursor, "Patrimonio Liquido")
    # --- Dados 2025 ---
    ativo_circulante_2025 = buscar_valor(cursor, "Ativo Circulante_2025")
    ativo_nao_circulante_2025 = buscar_valor(cursor, "Ativo Nao Circulante_2025")
    passivo_circulante_2025 = buscar_valor(cursor, "Passivo Circulante_2025")
    passivo_nao_circulante_2025 = buscar_valor(cursor, "Passivo Nao Circulante_2025")
    patrimonio_liquido_2025 = buscar_valor(cursor, "Patrimonio Liquido_2025")
    # --- Cálculos ---
    ativo_total = ativo_circulante + ativo_nao_circulante
    ativo_total_2025 = ativo_circulante_2025 + ativo_nao_circulante_2025
    passivo_total = passivo_circulante + passivo_nao_circulante
    passivo_total_2025 = passivo_circulante_2025 + passivo_nao_circulante_2025
    # Variações percentuais
    var_ac = ((ativo_circulante - ativo_circulante_2025) / ativo_circulante_2025) * 100 if ativo_circulante_2025 else 0
    var_anc = ((ativo_nao_circulante - ativo_nao_circulante_2025) / ativo_nao_circulante_2025) * 100 if ativo_nao_circulante_2025 else 0
    var_at = ((ativo_total - ativo_total_2025) / ativo_total_2025) * 100 if ativo_total_2025 else 0
    var_pc = ((passivo_circulante - passivo_circulante_2025) / passivo_circulante_2025) * 100 if passivo_circulante_2025 else 0
    var_pnc = ((passivo_nao_circulante - passivo_nao_circulante_2025) / passivo_nao_circulante_2025) * 100 if passivo_nao_circulante_2025 else 0
    var_pl = ((patrimonio_liquido - patrimonio_liquido_2025) / patrimonio_liquido_2025) * 100 if patrimonio_liquido_2025 else 0
    # Índices de Liquidez (2026)
    liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante else 0
    liquidez_geral = (ativo_circulante + ativo_nao_circulante) / (passivo_circulante + passivo_nao_circulante) if (passivo_circulante + passivo_nao_circulante) else 0
    endividamento_geral = (passivo_total / ativo_total) * 100 if ativo_total else 0
    participacao_capital_terceiros = (passivo_total / patrimonio_liquido) * 100 if patrimonio_liquido else 0
    # --- Exibição ---
    print("\n" + "="*70)
    print("📊 ANÁLISE DO BALANÇO PATRIMONIAL — 2026 vs 2025")
    print("="*70)
    print(f"{'Conta':<30} {'2025 (R$)':>15} {'2026 (R$)':>15} {'Var. (%)':>10}")
    print("-"*70)
    print(f"{'Ativo Circulante':<30} {ativo_circulante_2025:>15,.2f} {ativo_circulante:>15,.2f} {var_ac:>9.2f}%")
    print(f"{'Ativo Não Circulante':<30} {ativo_nao_circulante_2025:>15,.2f} {ativo_nao_circulante:>15,.2f} {var_anc:>9.2f}%")
    print(f"{'Ativo Total':<30} {ativo_total_2025:>15,.2f} {ativo_total:>15,.2f} {var_at:>9.2f}%")
    print(f"{'Passivo Circulante':<30} {passivo_circulante_2025:>15,.2f} {passivo_circulante:>15,.2f} {var_pc:>9.2f}%")
    print(f"{'Passivo Não Circulante':<30} {passivo_nao_circulante_2025:>15,.2f} {passivo_nao_circulante:>15,.2f} {var_pnc:>9.2f}%")
    print(f"{'Patrimônio Líquido':<30} {patrimonio_liquido_2025:>15,.2f} {patrimonio_liquido:>15,.2f} {var_pl:>9.2f}%")
    print("="*70)
    print("\n📈 ÍNDICES ECONÔMICO-FINANCEIROS (2026)")
    print("-"*50)
    print(f"Liquidez Corrente:........ {liquidez_corrente:.2f}")
    print(f"Liquidez Geral:........... {liquidez_geral:.2f}")
    print(f"Endividamento Geral:...... {endividamento_geral:.2f}%")
    print(f"Part. Capital Terceiros:.. {participacao_capital_terceiros:.2f}%")
    print("="*70)
    cursor.close()
    conn.close()
if __name__ == "__main__":
    analisar_bp()
