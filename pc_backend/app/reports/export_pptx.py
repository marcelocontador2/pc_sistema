from pptx import Presentation
import psycopg2
import os
from datetime import datetime
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
def formatar_mi(valor):
    return f"R$ {valor / 1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
def gerar_pptx():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    ativo_circulante_2026 = buscar_valor(cursor, "Ativo Circulante", 2026)
    ativo_nao_circulante_2026 = buscar_valor(cursor, "Ativo Nao Circulante", 2026)
    passivo_circulante_2026 = buscar_valor(cursor, "Passivo Circulante", 2026)
    passivo_nao_circulante_2026 = buscar_valor(cursor, "Passivo Nao Circulante", 2026)
    patrimonio_liquido_2026 = buscar_valor(cursor, "Patrimonio Liquido", 2026)
    receita_realizada_2026 = buscar_valor(cursor, "Receita Realizada", 2026)
    despesa_empenhada_2026 = buscar_valor(cursor, "Despesa Empenhada", 2026)
    superavit_patrimonial_2026 = buscar_valor(cursor, "Superavit Patrimonial", 2026)
    variacoes_ativas_2026 = buscar_valor(cursor, "Variacoes Ativas", 2026)
    ativo_circulante_2025 = buscar_valor(cursor, "Ativo Circulante", 2025)
    ativo_nao_circulante_2025 = buscar_valor(cursor, "Ativo Nao Circulante", 2025)
    passivo_circulante_2025 = buscar_valor(cursor, "Passivo Circulante", 2025)
    passivo_nao_circulante_2025 = buscar_valor(cursor, "Passivo Nao Circulante", 2025)
    patrimonio_liquido_2025 = buscar_valor(cursor, "Patrimonio Liquido", 2025)
    receita_realizada_2025 = buscar_valor(cursor, "Receita Realizada", 2025)
    despesa_empenhada_2025 = buscar_valor(cursor, "Despesa Empenhada", 2025)
    ativo_total_2026 = ativo_circulante_2026 + ativo_nao_circulante_2026
    ativo_total_2025 = ativo_circulante_2025 + ativo_nao_circulante_2025
    passivo_total_2026 = passivo_circulante_2026 + passivo_nao_circulante_2026
    passivo_total_2025 = passivo_circulante_2025 + passivo_nao_circulante_2025
    superavit_orcamentario_2026 = receita_realizada_2026 - despesa_empenhada_2026
    superavit_orcamentario_2025 = receita_realizada_2025 - despesa_empenhada_2025
    superavit_financeiro_2026 = ativo_total_2026 - passivo_total_2026
    def calc_var(atual, anterior):
        if anterior == 0: return 0.0
        return ((atual - anterior) / anterior) * 100
    var_rr = calc_var(receita_realizada_2026, receita_realizada_2025)
    var_de = calc_var(despesa_empenhada_2026, despesa_empenhada_2025)
    var_so = calc_var(superavit_orcamentario_2026, superavit_orcamentario_2025)
    liquidez_corrente = ativo_circulante_2026 / passivo_circulante_2026 if passivo_circulante_2026 else 0
    endividamento_geral = (passivo_total_2026 / ativo_total_2026) * 100 if ativo_total_2026 else 0
    margem_patrimonial = (superavit_patrimonial_2026 / variacoes_ativas_2026) * 100 if variacoes_ativas_2026 else 0
    substituicoes = {
        "R$ 39,3 mi": formatar_mi(superavit_orcamentario_2026),
        "R$ 37,5 mi": formatar_mi(superavit_patrimonial_2026),
        "R$ 63,0 mi": formatar_mi(superavit_financeiro_2026),
        "R$ 625,6 mi": formatar_mi(patrimonio_liquido_2026),
        "R$ 636,8 mi": formatar_mi(ativo_total_2026),
        "R$ 11,2 mi": formatar_mi(passivo_total_2026),
        "R$ 321,9 mi": formatar_mi(receita_realizada_2026),
        "R$ 140,39 mi": formatar_mi(receita_realizada_2026),
        "Alta liquidez (Liquidez Corrente > 29)": f"Alta liquidez (Liquidez Corrente > {liquidez_corrente:.1f})",
        "Baixíssimo endividamento (1,75%)": f"Baixíssimo endividamento ({endividamento_geral:.2f}%)",
        "Conclusão:  posição financeira extremamente sólida e de baixo risco.": f"Conclusão: posição financeira extremamente sólida e de baixo risco (Liquidez Corrente de {liquidez_corrente:.2f}).",
    }
    caminho_entrada = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\templates\Cofen_Analise_Demonstracoes_Contabeis_1S2026 (10082026).pptx"
    prs = Presentation(caminho_entrada)
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    texto_original = paragraph.text
                    texto_novo = texto_original
                    for chave, valor in substituicoes.items():
                        if chave in texto_novo:
                            texto_novo = texto_novo.replace(chave, valor)
                    if texto_novo != texto_original:
                        # Limpa todos os runs e recria um único run com o novo texto
                        for run in paragraph.runs:
                            run.text = ""
                        if paragraph.runs:
                            paragraph.runs[0].text = texto_novo
                        else:
                            paragraph.add_run().text = texto_novo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = f"C:\\Users\\Marcelo Medeiros\\pc_sistema\\pc_storage\\output_documentos\\analise_cofen_{timestamp}.pptx"
    prs.save(caminho_saida)
    print(f"PPTX gerado com sucesso: {caminho_saida}")
    cursor.close()
    conn.close()
if __name__ == "__main__":
    gerar_pptx()
