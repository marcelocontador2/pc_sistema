import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Substitui a lista linksParaMover pela ordem desejada
    padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
    match = padrao.search(c)
    if match:
        lista_nova = """[
        'Conferência das Demonstrações',
        'Integridade entre Demonstrações',
        'Análise BP',
        'Análise Orçamentária (BO)',
        'Análise Financeira (BF)',
        'Análise DFC',
        'Análise Patrimonial (DVP)',
        'Índices de Liquidez',
        'Composição Receitas/Despesas',
        'Resultados Gerais',
        'Comparativo de Receitas',
        'Comparativo de Despesas',
        'Análise por Centro de Custos',
        'Custo de Pessoal'
    ]"""
        c = c[:match.start(2)] + lista_nova + c[match.end(2):]
        print(f"[OK] {arq} - Lista linksParaMover reorganizada.")

    # 2. Garante que os links estao no HTML estatico (na ordem correta)
    # Procura o bloco de links de analise e substitui pela ordem correta
    idx_conf = c.find('Conferência das Demonstrações')
    if idx_conf != -1:
        start_bloco = c.rfind('<a', 0, idx_conf)
        if start_bloco == -1:
            start_bloco = idx_conf

        idx_comp = c.find('Comparativo de Despesas', idx_conf)
        if idx_comp != -1:
            end_bloco = c.find('</a>', idx_comp) + 4
            if end_bloco == -1:
                end_bloco = idx_comp + 100

            bloco_novo = '''<a href="/conferencia" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Conferência das Demonstrações</a>
            <a href="/integridade" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Integridade entre Demonstrações</a>
            <a href="/analise_bp" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise BP</a>
            <a href="/analise_orcamentaria" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a>
            <a href="/analise_financeira_bf" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Financeira (BF)</a>
            <a href="/analise_dfc" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise DFC</a>
            <a href="/analise_patrimonial" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a>
            <a href="/liquidez" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Índices de Liquidez</a>
            <a href="/composicao_receitas_despesas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Composição Receitas/Despesas</a>
            <a href="/resultados_gerais" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Resultados Gerais</a>
            <a href="/comparativo_receitas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Comparativo de Receitas</a>
            <a href="/comparativo_despesas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Comparativo de Despesas</a>
            <a href="/centro_custos" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise por Centro de Custos</a>
            <a href="/custo_pessoal" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Custo de Pessoal</a>'''

            c = c[:start_bloco] + bloco_novo + c[end_bloco:]
            print(f"[OK] {arq} - Bloco de links reorganizado.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_ordem_menu_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
