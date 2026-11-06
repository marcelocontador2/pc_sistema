import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

# Bloco de itens de análise com o titulo
bloco_analises = '''
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

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # Localiza o final do <li> do Relatorio Consolidado
    idx = c.find('Relatorio Consolidado')
    if idx == -1:
        print(f"[AVISO] {arq} nao encontrei 'Relatorio Consolidado'.")
        continue

    end_li = c.find('</li>', idx) + 5
    if end_li == -1:
        print(f"[AVISO] {arq} nao encontrei o </li>.")
        continue

    # Remove todos os <li> de analise que estão logo depois (para nao duplicar)
    # Pega do end_li até o proximo <li> de "Demonstrações" ou proximo bloco
    trecho_seguinte = c[end_li:]
    # Remove tudo que for link de analise ou titulo de analise
    import re
    trecho_seguinte = re.sub(r'<li[^>]*>.*?(?:Análise|Conferência|Integridade|Composição|Liquidez|Resultados|Custo|Comparativo).*?</li>', '', trecho_seguinte, flags=re.DOTALL)
    
    # Agora insere o bloco novo logo apos o end_li
    c = c[:end_li] + bloco_analises + trecho_seguinte

    shutil.copy2(arq, f"{arq}.bak_menu_final_{ts}")
    open(arq, "w", encoding="utf-8").write(c)
    alterados += 1
    print(f"[OK] {arq} - Menu de Analises refeito com titulo e itens limpos.")

print(f"\n[OK] {alterados} arquivos alterados.")
