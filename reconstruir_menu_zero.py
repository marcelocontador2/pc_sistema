import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

# Menu completo no padrao do sistema
menu_html = '''
<nav style="width: 250px; background: white; padding: 20px; height: 100vh; border-right: 1px solid #ddd; float: left; box-sizing: border-box;">
    <div style="margin-bottom: 20px;">
        <img src="/static_logos/logo_cofen.png" style="max-height: 50px;" onerror="this.style.display='none'">
    </div>
    <ul style="list-style: none; padding: 0; margin: 0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px;">
        <li style="margin-bottom: 15px;"><a href="/importar" style="text-decoration: none; color: #333; font-weight: bold;">Importar Relatórios</a></li>
        <li style="margin-bottom: 15px;"><a href="/base_legal" style="text-decoration: none; color: #333; font-weight: bold;">Base Legal</a></li>
        <li style="margin-bottom: 15px;"><a href="/configuracoes" style="text-decoration: none; color: #333; font-weight: bold;">Configurações</a></li>
        <li style="margin-bottom: 15px;"><a href="/relatorio_consolidado" style="text-decoration: none; color: #333; font-weight: bold;">Relatório Consolidado</a></li>
        <li style="margin-bottom: 10px;">
            <a href="#" style="text-decoration: none; color: #003366; font-weight: bold; display: block; margin-bottom: 10px;">Análises Contábeis</a>
            <ul style="list-style: none; padding-left: 15px; margin: 0;">
                <li style="margin-bottom: 8px;"><a href="/conferencia" style="text-decoration: none; color: #555;">Conferência das Demonstrações</a></li>
                <li style="margin-bottom: 8px;"><a href="/integridade" style="text-decoration: none; color: #555;">Integridade entre Demonstrações</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_orcamentaria" style="text-decoration: none; color: #555;">Análise Orçamentária (BO)</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_financeira_bf" style="text-decoration: none; color: #555;">Análise Financeira (BF)</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_dfc" style="text-decoration: none; color: #555;">Análise DFC</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_patrimonial" style="text-decoration: none; color: #555;">Análise Patrimonial (DVP)</a></li>
                <li style="margin-bottom: 8px;"><a href="/composicao_receitas_despesas" style="text-decoration: none; color: #555;">Composição Receitas/Despesas</a></li>
                <li style="margin-bottom: 8px;"><a href="/liquidez" style="text-decoration: none; color: #555;">Índices de Liquidez</a></li>
                <li style="margin-bottom: 8px;"><a href="/resultados_gerais" style="text-decoration: none; color: #555;">Resultados Gerais</a></li>
                <li style="margin-bottom: 8px;"><a href="/custo_pessoal" style="text-decoration: none; color: #555;">Custo de Pessoal</a></li>
                <li style="margin-bottom: 8px;"><a href="/centro_custos" style="text-decoration: none; color: #555;">Análise por Centro de Custos</a></li>
                <li style="margin-bottom: 8px;"><a href="/comparativo_receitas" style="text-decoration: none; color: #555;">Comparativo de Receitas</a></li>
                <li style="margin-bottom: 8px;"><a href="/comparativo_despesas" style="text-decoration: none; color: #555;">Comparativo de Despesas</a></li>
            </ul>
        </li>
    </ul>
</nav>
<div style="margin-left: 250px; padding: 20px;">
'''

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # 1. Remove QUALQUER menu antigo que esteja entre <nav>...</nav> ou <div id="menu">...</div>
    c = re.sub(r'<nav[^>]*>.*?</nav>', '', c, flags=re.DOTALL)
    c = re.sub(r'<div[^>]*id="menu"[^>]*>.*?</div>', '', c, flags=re.DOTALL)

    # 2. Remove qualquer bloco antigo de menu que tenha "Análises Contábeis" (para não duplicar)
    # (Isso é perigoso, mas como o menu está quebrado, melhor garantir)
    c = re.sub(r'<ul[^>]*>.*?Análises Contábeis.*?</ul>', '', c, flags=re.DOTALL)

    # 3. Insere o menu novo logo após o <body>
    idx_body = c.find('<body')
    if idx_body != -1:
        fim_body = c.find('>', idx_body) + 1
        c = c[:fim_body] + '\n' + menu_html + c[fim_body:]
        
        shutil.copy2(arq, f"{arq}.bak_reconstruir_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - Menu reconstruido do zero.")
    else:
        print(f"[AVISO] {arq} - nao encontrei a tag <body>.")

print(f"\n[OK] {alterados} arquivos alterados.")
