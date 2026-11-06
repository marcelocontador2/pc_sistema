import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

menu_novo = '''<aside class="sidebar">
  <div class="logo-area"><img src="/pc_frontend/logo-cofen.png" alt="Logo COFEN" style="max-height: 40px; width: auto; display: block;"></div>
  <ul style="padding-left: 60px; margin-left: 0; list-style: none;">
    <li><a href="#" id="menu-upload" onclick="mostrarTela('upload')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar Relatórios</a></li>
    <li><a href="/base_legal" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Base Legal</a></li>
    <li><a href="/configuracoes" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Configurações</a></li>
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
  </ul>
</aside>'''

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    c = open(arq, encoding="utf-8", errors="ignore").read()
    padrao = re.compile(r'<aside class="sidebar">.*?</aside>', re.DOTALL)
    if padrao.search(c):
        c = padrao.sub(menu_novo, c, count=1)
        shutil.copy2(arq, f"{arq}.bak_menu_final_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Menu substituido por completo.")
    else:
        print(f"[AVISO] {arq} - nao encontrei a tag aside sidebar.")

print("\n[OK] Processo concluido. Teste no navegador com Ctrl+Shift+R.")
