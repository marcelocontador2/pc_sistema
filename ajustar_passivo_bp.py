import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_passivo_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Substitui o bloco de render para incluir 'Passivo Total' e 'Total do Passivo'
antigo = """let html = '';
            html += linha('Ativo Circulante', d.ativo_circulante.atual, d.ativo_circulante.anterior);
            html += linha('Caixa e Equivalentes', d.caixa.atual, d.caixa.anterior);
            html += linha('Créditos a Curto Prazo', d.creditos.atual, d.creditos.anterior);
            html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Ativo Realizável a Longo Prazo', d.ativo_realizavel.atual, d.ativo_realizavel.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);
            html += linha('TOTAL DO ATIVO', d.total_ativo.atual, d.total_ativo.anterior);
            html += linha('Passivo Circulante', d.passivo_circulante.atual, d.passivo_circulante.anterior);
            html += linha('Passivo Não Circulante', d.passivo_nao_circulante.atual, d.passivo_nao_circulante.anterior);
            html += linha('TOTAL DO PASSIVO', d.total_passivo.atual, d.total_passivo.anterior);
            html += linha('Patrimônio Líquido', d.patrimonio_liquido.atual, d.patrimonio_liquido.anterior);
            tb.innerHTML = html;"""

novo = """let html = '';
            html += linha('Ativo Circulante', d.ativo_circulante.atual, d.ativo_circulante.anterior);
            html += linha('Caixa e Equivalentes', d.caixa.atual, d.caixa.anterior);
            html += linha('Créditos a Curto Prazo', d.creditos.atual, d.creditos.anterior);
            html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Ativo Realizável a Longo Prazo', d.ativo_realizavel.atual, d.ativo_realizavel.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);
            html += linha('TOTAL DO ATIVO', d.total_ativo.atual, d.total_ativo.anterior);
            html += linha('Passivo Circulante', d.passivo_circulante.atual, d.passivo_circulante.anterior);
            html += linha('Passivo Não Circulante', d.passivo_nao_circulante.atual, d.passivo_nao_circulante.anterior);
            html += linha('Passivo Total', d.passivo_total.atual, d.passivo_total.anterior);
            html += linha('Patrimônio Líquido', d.patrimonio_liquido.atual, d.patrimonio_liquido.anterior);
            html += linha('TOTAL DO PASSIVO', d.total_passivo.atual, d.total_passivo.anterior);
            tb.innerHTML = html;"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Frontend ajustado: 'Passivo Total' e 'Total do Passivo' (com PL).")
else:
    print("[AVISO] Trecho do render nao encontrado. Tentando variacao...")
    # Tenta substituir apenas a linha do TOTAL DO PASSIVO
    c = c.replace(
        "html += linha('TOTAL DO PASSIVO', d.total_passivo.atual, d.total_passivo.anterior);",
        "html += linha('Passivo Total', d.passivo_total.atual, d.passivo_total.anterior);\n            html += linha('TOTAL DO PASSIVO', d.total_passivo.atual, d.total_passivo.anterior);"
    )
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Frontend ajustado (variacao).")
