import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove todos os <li> que contenham "Análise Orçamentária" (duplicatas)
    # Vamos usar regex para remover o bloco <li>...</li> que tenha "Análise Orçamentária"
    padrao_orc = re.compile(
        r'<li[^>]*>\s*<a[^>]*>Análise Orçamentária</a>.*?</li>',
        re.DOTALL
    )
    c = padrao_orc.sub('', c)
    
    # 2. Depois de remover TODOS os <li> de análise, vamos colocar UM bloco limpo
    # no lugar do "Relatorio Consolidado" (ou de "Configuracoes")
    # Vamos procurar o "Configuracoes" e inserir o bloco depois
    idx_config = c.find('Configuracoes</a>')
    if idx_config == -1:
        idx_config = c.find('Base Legal</a>')
    
    if idx_config != -1:
        end_li = c.find('</li>', idx_config) + 5
        if end_li != -1:
            bloco_limpo = '''
    <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>
    <li style="margin-top: 15px;">
      <a style="display:block; padding:10px 0px; text-decoration:none; color:#003366; font-weight:bold; border-bottom: 2px solid #eee;">Análises Contábeis</a>
    </li>
    <li><a href="/conferencia" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Conferência das Demonstrações</a></li>
    <li><a href="/integridade" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Integridade entre Demonstrações</a></li>
    <li><a href="/analise_orcamentaria" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a></li>
    <li><a href="/analise_financeira_bf" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Financeira (BF)</a></li>
    <li><a href="/analise_dfc" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise DFC</a></li>
    <li><a href="/analise_patrimonial" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a></li>
    <li><a href="/composicao_receitas_despesas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Composição Receitas/Despesas</a></li>
    <li><a href="/liquidez" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Índices de Liquidez</a></li>
    <li><a href="/resultados_gerais" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Resultados Gerais</a></li>
    <li><a href="/custo_pessoal" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Custo de Pessoal</a></li>
    <li><a href="/centro_custos" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise por Centro de Custos</a></li>
    <li><a href="/comparativo_receitas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Comparativo de Receitas</a></li>
    <li><a href="/comparativo_despesas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Comparativo de Despesas</a></li>
'''
            c = c[:end_li] + bloco_limpo + c[end_li:]

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_final_limpeza_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - Menu limpo e reorganizado (sem duplicatas).")

print(f"\n[OK] {alterados} arquivos alterados.")
