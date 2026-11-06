import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove a DUPLICATA do título "Análises Contábeis" que está no final
    # (ele aparece sozinho como último <li> do menu)
    padrao_dup = re.compile(
        r'<li[^>]*>\s*<a[^>]*>\s*Análises Contábeis\s*</a>\s*</li>\s*$',
        re.MULTILINE
    )
    # Remove o último <li> de "Análises Contábeis" (se for o último item do menu)
    c = re.sub(r'<li[^>]*>\s*<a[^>]*>\s*Análises Contábeis\s*</a>\s*</li>\s*(?=</ul>)', '', c, count=1)

    # 2. Remove a DUPLICATA do título "Análises Contábeis" que está antes dos itens
    # (o primeiro que aparece)
    c = re.sub(r'<li[^>]*>\s*<a[^>]*>\s*Análises Contábeis\s*</a>\s*</li>\s*', '', c, count=1)

    # 3. Agora que os títulos foram removidos, remove os itens de análise que ficaram soltos
    # (para depois recriar tudo limpo)
    padrao_itens = re.compile(
        r'<li[^>]*>.*?(?:Conferência das Demonstrações|Integridade entre Demonstrações|Análise Orçamentária|Análise Financeira|Análise DFC|Análise Patrimonial|Composição Receitas|Índices de Liquidez|Resultados Gerais|Custo de Pessoal|Análise por Centro de Custos|Comparativo de Receitas|Comparativo de Despesas).*?</li>',
        re.DOTALL
    )
    c = padrao_itens.sub('', c)

    # 4. Localiza o "Relatório Consolidado" (que é o último item antes das análises)
    idx = c.find('Relatório Consolidado')
    if idx == -1:
        idx = c.find('Relatorio Consolidado')
    
    if idx != -1:
        end_li = c.find('</li>', idx) + 5
        if end_li != -1:
            # 5. Monta o bloco COMPLETO do submenu expansível
            bloco_final = '''
    <li>
      <a href="javascript:void(0)" onclick="toggleSubmenuAnalises(this)" style="display:block; padding:10px 0px; text-decoration:none; color:#003366; font-weight:bold; border-bottom: 2px solid #eee;">Análises Contábeis <span style="float:right;">&#9660;</span></a>
      <ul id="submenu-analises" style="list-style: none; padding-left: 15px; margin: 0; display: none;">
        <li><a href="/conferencia" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Conferência das Demonstrações</a></li>
        <li><a href="/integridade" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Integridade entre Demonstrações</a></li>
        <li><a href="/analise_orcamentaria" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a></li>
        <li><a href="/analise_financeira_bf" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Análise Financeira (BF)</a></li>
        <li><a href="/analise_dfc" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Análise DFC</a></li>
        <li><a href="/analise_patrimonial" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a></li>
        <li><a href="/composicao_receitas_despesas" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Composição Receitas/Despesas</a></li>
        <li><a href="/liquidez" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Índices de Liquidez</a></li>
        <li><a href="/resultados_gerais" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Resultados Gerais</a></li>
        <li><a href="/custo_pessoal" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Custo de Pessoal</a></li>
        <li><a href="/centro_custos" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Análise por Centro de Custos</a></li>
        <li><a href="/comparativo_receitas" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Comparativo de Receitas</a></li>
        <li><a href="/comparativo_despesas" style="display:block; padding:8px 0; text-decoration:none; color:#555;">Comparativo de Despesas</a></li>
      </ul>
    </li>
'''
            c = c[:end_li] + bloco_final + c[end_li:]

    # 6. Adiciona a função JS (se não existir)
    if 'function toggleSubmenuAnalises' not in c:
        script_js = '''
<script>
function toggleSubmenuAnalises(el) {
    const submenu = document.getElementById('submenu-analises');
    if (submenu) {
        if (submenu.style.display === 'none' || submenu.style.display === '') {
            submenu.style.display = 'block';
            el.querySelector('span').innerHTML = '&#9650;';
        } else {
            submenu.style.display = 'none';
            el.querySelector('span').innerHTML = '&#9660;';
        }
    }
}
</script>
'''
        idx_body = c.rfind('</body>')
        if idx_body != -1:
            c = c[:idx_body] + script_js + c[idx_body:]

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_correcao_final_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - Menu reorganizado com submenu expansível.")

print(f"\n[OK] {alterados} arquivos alterados.")
