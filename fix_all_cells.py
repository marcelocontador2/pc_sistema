import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_all_cells_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Lista de substituições diretas (linha por linha, usando o texto exato)
substituicoes = [
    # Linha 349 - período (tem acento em "Exercício", "Março")
    (
        'pdf.cell(85, 6, f"Período: {periodo_formatado}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")',
        'pdf.cell(85, 6, _limpar_ascii(f"Período: {periodo_formatado}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")'
    ),
    # Linha 358 - continuação (tem acento em "Continuação")
    (
        'pdf.cell(0, 5, f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)",',
        'pdf.cell(0, 5, _limpar_ascii(f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)"),'
    ),
]

# Aplica cada substituição
for antigo, novo in substituicoes:
    if antigo in c:
        c = c.replace(antigo, novo, 1)
        print(f"[OK] Substituído: {antigo[:80]}...")
    else:
        print(f"[AVISO] Não encontrado: {antigo[:80]}...")

# 3. Também corrige o título_pdf e headers na origem (onde são definidos)
# Substitui os acentos corrompidos por versões limpas
c = c.replace('titulo_pdf = "Balancete Contábil"', 'titulo_pdf = "Balancete Contabil"')
c = c.replace('titulo_pdf = "Balanço Patrimonial"', 'titulo_pdf = "Balanco Patrimonial"')
c = c.replace('titulo_pdf = "Balanço Financeiro"', 'titulo_pdf = "Balanco Financeiro"')
c = c.replace('titulo_pdf = "Balanço Orçamentário"', 'titulo_pdf = "Balanco Orcamentario"')
c = c.replace('titulo_pdf = "Demonstração das Mutações do Patrimônio Líquido"', 'titulo_pdf = "Demonstracao das Mutacoes do Patrimonio Liquido"')
c = c.replace('titulo_pdf = "Demonstração do Fluxo de Caixa"', 'titulo_pdf = "Demonstracao do Fluxo de Caixa"')
c = c.replace('titulo_pdf = "Demonstração das Variações Patrimoniais"', 'titulo_pdf = "Demonstracao das Variacoes Patrimoniais"')
c = c.replace('titulo_pdf = "Balanço Comparativo"', 'titulo_pdf = "Balanco Comparativo"')

# Também corrige os headers que têm acentos
c = c.replace('"SALDO ANTERIOR", "DÉBITOS", "CRÉDITOS", "SALDO"', '"SALDO ANTERIOR", "DEBITOS", "CREDITOS", "SALDO"')
c = c.replace('"ESPECIFICAÇÃO (ATIVO)"', '"ESPECIFICACAO (ATIVO)"')
c = c.replace('"ESPECIFICAÇÃO (PASSIVO)"', '"ESPECIFICACAO (PASSIVO)"')
c = c.replace('"ESPECIFICAÇÃO (INGRESSOS)"', '"ESPECIFICACAO (INGRESSOS)"')
c = c.replace('"ESPECIFICAÇÃO (DISPÊNDIOS)"', '"ESPECIFICACAO (DISPENDIOS)"')
c = c.replace('"ESPECIFICAÇÃO", "PREVISÃO INICIAL", "PREVISÃO ATUALIZADA", "RECEITA REALIZADA", "SALDO", "DESPESAS", "SALDO FINAL"', '"ESPECIFICACAO", "PREVISAO INICIAL", "PREVISAO ATUALIZADA", "RECEITA REALIZADA", "SALDO", "DESPESAS", "SALDO FINAL"')
c = c.replace('"ESPECIFICAÇÃO", "PATRIMÔNIO SOCIAL", "ADIANTAMENTO P/ AUMENTO"', '"ESPECIFICACAO", "PATRIMONIO SOCIAL", "ADIANTAMENTO P/ AUMENTO"')
c = c.replace('"RESERVAS DE CAPITAL", "AJUSTES DE AVALIAÇÃO", "RESERVAS DE LUCROS"', '"RESERVAS DE CAPITAL", "AJUSTES DE AVALIACAO", "RESERVAS DE LUCROS"')
c = c.replace('"VARIAÇÕES AUMENTATIVAS"', '"VARIACOES AUMENTATIVAS"')
c = c.replace('"VARIAÇÕES DIMINUTIVAS"', '"VARIACOES DIMINUTIVAS"')

print("[OK] Títulos e headers limpos de acentos")

# Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_all_cells_{ts}", back_path)
    print("[OK] Backup restaurado")
