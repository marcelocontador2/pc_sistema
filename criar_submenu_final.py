import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # 1. Remove TODOS os <li> de análise (que estão soltos no nível principal)
    # (Usamos regex para pegar os links de análise)
    padrao = re.compile(
        r'<li[^>]*>.*?(?:Análise Orçamentária|Análise Financeira|Análise DFC|Análise Patrimonial|Conferência das Demonstrações|Integridade entre Demonstrações|Composição Receitas|Índices de Liquidez|Resultados Gerais|Custo de Pessoal|Centro de Custos|Comparativo de Receitas|Comparativo de Despesas).*?</li>',
        re.DOTALL
    )
    c = padrao.sub('', c)

    # 2. Remove o título antigo "Análises Contábeis" (que estava solto)
    c = re.sub(r'<li[^>]*>\s*<a[^>]*>Análises Contábeis</a>\s*</li>', '', c)

    # 3. Localiza o link do "Relatorio Consolidado" (sem acento, como está no HTML)
    idx = c.find('Relatorio Consolidado')
    if idx == -1:
        # Tenta com acento, por garantia
        idx = c.find('Relatório Consolidado')
    
    if idx == -1:
        print(f"[AVISO] {arq} nao encontrei 'Relatorio Consolidado'.")
        continue

    # Encontra o final do </li> do Relatorio Consolidado
    end_li = c.find('</li>', idx) + 5
    if end_li == -1:
        print(f"[AVISO] {arq} nao encontrei o </li>.")
        continue

    # 4. Monta o bloco do submenu expansível
    submenu_completo = '''
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

    # 5. Insere o bloco completo após o Relatorio Consolidado
    c = c[:end_li] + submenu_completo + c[end_li:]

    # 6. Adiciona a função JS para abrir/fechar o submenu (se ainda não existir)
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
        else:
            c += script_js

    shutil.copy2(arq, f"{arq}.bak_submenu_final_{ts}")
    open(arq, "w", encoding="utf-8").write(c)
    alterados += 1
    print(f"[OK] {arq} - Submenu 'Análises Contábeis' criado (expansível).")

print(f"\n[OK] {alterados} arquivos alterados.")
