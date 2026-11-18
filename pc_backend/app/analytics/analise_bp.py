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
def buscar_valor(cursor, grupo, periodo_id):
    """Busca o valor de uma conta num periodo especifico."""
    cursor.execute(
        "SELECT valor_atual FROM demonstracao_resumo "
        "WHERE grupo_demonstrativo = %s AND periodo_id = %s "
        "ORDER BY id DESC LIMIT 1;",
        (grupo, periodo_id)
    )
    resultado = cursor.fetchone()
    return float(resultado[0]) if resultado else 0.0


def get_periodo_id(cursor, ano):
    """Retorna o id do periodo Jan-Set do ano informado."""
    cursor.execute(
        "SELECT id FROM periodo WHERE ano = %s AND periodo_acumulado = %s;",
        (ano, "Jan-Set")
    )
    res = cursor.fetchone()
    return res[0] if res else None


def analisar_bp():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    pid_2026 = get_periodo_id(cursor, 2026)
    pid_2025 = get_periodo_id(cursor, 2025)
    if not pid_2026:
        print("ERRO: periodo 2026 nao encontrado")
        cursor.close(); conn.close()
        return
    if not pid_2025:
        print("AVISO: periodo 2025 nao encontrado, usando zeros")
        pid_2025 = "00000000-0000-0000-0000-000000000000"

    # Lista de todas as contas que o frontend espera
    contas = [
        "Ativo Circulante",
        "Caixa e Equivalentes",
        "Creditos a Curto Prazo",
        "Demais Creditos Curto Prazo",
        "Estoques",
        "Variacoes Patrimoniais Antecipadas",
        "Ativo Nao Circulante",
        "Ativo Realizavel Longo Prazo",
        "Creditos a Longo Prazo",
        "Creditos Tributarios a Receber",
        "Divida Ativa Nao Tributaria",
        "Demais Creditos Longo Prazo",
        "Imobilizado",
        "Bens Moveis",
        "Bens Imoveis",
        "Intangivel",
        "Softwares",
        "Passivo Circulante",
        "Obrigacoes Trabalhistas Curto Prazo",
        "Fornecedores Curto Prazo",
        "Obrigacoes Fiscais Curto Prazo",
        "Provisoes Curto Prazo",
        "Demais Obrigacoes Curto Prazo",
        "Passivo Nao Circulante",
        "Provisoes Longo Prazo",
        "Patrimonio Liquido",
        "Total Geral",
    ]

    # Buscar todos os valores de uma vez (mais eficiente)
    valores_2026 = {}
    valores_2025 = {}
    for conta in contas:
        valores_2026[conta] = buscar_valor(cursor, conta, pid_2026)
        valores_2025[conta] = buscar_valor(cursor, conta, pid_2025)

    # Atalhos para as contas macro
    ativo_circulante = valores_2026["Ativo Circulante"]
    ativo_nao_circulante = valores_2026["Ativo Nao Circulante"]
    passivo_circulante = valores_2026["Passivo Circulante"]
    passivo_nao_circulante = valores_2026["Passivo Nao Circulante"]
    patrimonio_liquido = valores_2026["Patrimonio Liquido"]

    ativo_circulante_2025 = valores_2025["Ativo Circulante"]
    ativo_nao_circulante_2025 = valores_2025["Ativo Nao Circulante"]
    passivo_circulante_2025 = valores_2025["Passivo Circulante"]
    passivo_nao_circulante_2025 = valores_2025["Passivo Nao Circulante"]
    patrimonio_liquido_2025 = valores_2025["Patrimonio Liquido"]

    # Calculos
    ativo_total = ativo_circulante + ativo_nao_circulante
    ativo_total_2025 = ativo_circulante_2025 + ativo_nao_circulante_2025
    passivo_total = passivo_circulante + passivo_nao_circulante
    passivo_total_2025 = passivo_circulante_2025 + passivo_nao_circulante_2025

    def _var(atual, anterior):
        if anterior and anterior != 0:
            return ((atual - anterior) / anterior) * 100
        return 0.0

    var_ac = _var(ativo_circulante, ativo_circulante_2025)
    var_anc = _var(ativo_nao_circulante, ativo_nao_circulante_2025)
    var_at = _var(ativo_total, ativo_total_2025)
    var_pc = _var(passivo_circulante, passivo_circulante_2025)
    var_pnc = _var(passivo_nao_circulante, passivo_nao_circulante_2025)
    var_pl = _var(patrimonio_liquido, patrimonio_liquido_2025)

    # Indices
    liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante else 0
    liquidez_geral = (ativo_circulante + ativo_nao_circulante) / (passivo_circulante + passivo_nao_circulante) if (passivo_circulante + passivo_nao_circulante) else 0
    endividamento_geral = (passivo_total / ativo_total) * 100 if ativo_total else 0
    participacao_capital_terceiros = (passivo_total / patrimonio_liquido) * 100 if patrimonio_liquido else 0

    # Exibicao (mantida igual)
    print("\n" + "="*70)
    print("ANALISE DO BALANCO PATRIMONIAL - 2026 vs 2025")
    print("="*70)
    print(f"{'Conta':<30} {'2025 (R$)':>15} {'2026 (R$)':>15} {'Var. (%)':>10}")
    print("-"*70)
    print(f"{'Ativo Circulante':<30} {ativo_circulante_2025:>15,.2f} {ativo_circulante:>15,.2f} {var_ac:>9.2f}%")
    print(f"{'Ativo Nao Circulante':<30} {ativo_nao_circulante_2025:>15,.2f} {ativo_nao_circulante:>15,.2f} {var_anc:>9.2f}%")
    print(f"{'Ativo Total':<30} {ativo_total_2025:>15,.2f} {ativo_total:>15,.2f} {var_at:>9.2f}%")
    print(f"{'Passivo Circulante':<30} {passivo_circulante_2025:>15,.2f} {passivo_circulante:>15,.2f} {var_pc:>9.2f}%")
    print(f"{'Passivo Nao Circulante':<30} {passivo_nao_circulante_2025:>15,.2f} {passivo_nao_circulante:>15,.2f} {var_pnc:>9.2f}%")
    print(f"{'Patrimonio Liquido':<30} {patrimonio_liquido_2025:>15,.2f} {patrimonio_liquido:>15,.2f} {var_pl:>9.2f}%")
    print("="*70)
    print("\nINDICES ECONOMICO-FINANCEIROS (2026)")
    print("-"*50)
    print(f"Liquidez Corrente:........ {liquidez_corrente:.2f}")
    print(f"Liquidez Geral:........... {liquidez_geral:.2f}")
    print(f"Endividamento Geral:...... {endividamento_geral:.2f}%")
    print(f"Part. Capital Terceiros:.. {participacao_capital_terceiros:.2f}%")
    print("="*70)

    # Retorno completo para o frontend
    resultado = {
        "2026": valores_2026,
        "2025": valores_2025,
        "variacoes": {
            "ativo_circulante": var_ac,
            "ativo_nao_circulante": var_anc,
            "ativo_total": var_at,
            "passivo_circulante": var_pc,
            "passivo_nao_circulante": var_pnc,
            "patrimonio_liquido": var_pl,
        },
        "indices": {
            "liquidez_corrente": liquidez_corrente,
            "liquidez_geral": liquidez_geral,
            "endividamento_geral": endividamento_geral,
            "participacao_capital_terceiros": participacao_capital_terceiros,
        },
        "totais": {
            "ativo_total_2026": ativo_total,
            "ativo_total_2025": ativo_total_2025,
            "passivo_total_2026": passivo_total,
            "passivo_total_2025": passivo_total_2025,
        }
    }

    cursor.close()
    conn.close()
    return resultado


if __name__ == "__main__":
    analisar_bp()
