import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove o script antigo que constroi o submenu (o que tem "const novoLi")
    idx_script = c.find("const novoLi = document.createElement('li')")
    if idx_script != -1:
        # Encontra o inicio do <script> antes do novoLi
        inicio_script = c.rfind("<script>", 0, idx_script)
        if inicio_script == -1:
            inicio_script = idx_script

        # Encontra o fim do </script> depois do novoLi
        fim_script = c.find("</script>", idx_script) + 9
        if fim_script == -1:
            fim_script = idx_script + 3000

        # Remove o script inteiro
        c = c[:inicio_script] + c[fim_script:]
        print(f"[OK] {arq} - Script antigo de construcao do submenu removido.")

    # 2. Remove qualquer outro script que adicione itens ao submenu (setTimeout)
    padrao_timeout = re.compile(
        r'<script>\s*document\.addEventListener\("DOMContentLoaded",\s*function\(\)\s*\{.*?setTimeout.*?submenuAnalises.*?\}\);\s*\}\);\s*</script>',
        re.DOTALL
    )
    c = padrao_timeout.sub('', c)
    print(f"[OK] {arq} - Scripts setTimeout removidos.")

    # 3. Encontra o link do "Relatorio Consolidado" para inserir o novo submenu
    idx_rel = c.find('Relatorio Consolidado')
    if idx_rel == -1:
        idx_rel = c.find('Relatório Consolidado')

    if idx_rel == -1:
        print(f"[AVISO] {arq} - Nao encontrei o 'Relatorio Consolidado'.")
        continue

    # Encontra o fechamento do <li> do Relatorio Consolidado
    end_li = c.find('</li>', idx_rel) + 5
    if end_li == -1:
        print(f"[AVISO] {arq} - Nao encontrei o </li>.")
        continue

    # 4. Novo submenu com os links na ordem correta
    submenu_html = '''
    <li>
      <a href="#" style="display:block; padding:10px 0px; text-decoration:none; color:#003366; font-weight:bold; border-bottom: 2px solid #eee;">Análises Contábeis</a>
      <ul style="list-style: none; padding-left: 15px; margin: 0;">
        <li><a href="/conferencia" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Conferência das Demonstrações</a></li>
        <li><a href="/integridade" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Integridade entre Demonstrações</a></li>
        <li><a href="/analise_bp" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise BP</a></li>
        <li><a href="/analise_orcamentaria" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a></li>
        <li><a href="/analise_financeira_bf" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Financeira (BF)</a></li>
        <li><a href="/analise_dfc" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise DFC</a></li>
        <li><a href="/analise_patrimonial" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a></li>
        <li><a href="/liquidez" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Índices de Liquidez</a></li>
        <li><a href="/composicao_receitas_despesas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Composição Receitas/Despesas</a></li>
        <li><a href="/resultados_gerais" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Resultados Gerais</a></li>
        <li><a href="/comparativo_receitas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Comparativo de Receitas</a></li>
        <li><a href="/comparativo_despesas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Comparativo de Despesas</a></li>
        <li><a href="/centro_custos" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise por Centro de Custos</a></li>
        <li><a href="/custo_pessoal" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Custo de Pessoal</a></li>
      </ul>
    </li>
'''

    c = c[:end_li] + submenu_html + c[end_li:]
    print(f"[OK] {arq} - Novo submenu inserido no HTML (ordem correta).")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_submenu_fixo_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
