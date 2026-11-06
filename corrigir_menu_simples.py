import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_correcao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# O script vai buscar todo o bloco <li> do Relatório Consolidado (incluindo os subitens errados que eu criei)
# e substituir apenas pela tag <li> simples do link.
padrao = re.compile(
    r'(<li[^>]*>\s*<a[^>]*href="/relatorio_consolidado".*?)(?=<\/ul>)', # Pega do link até o fechamento do submenu que criei por engano
    re.DOTALL | re.IGNORECASE
)

# O jeito mais seguro: encontrar a tag exata e apagar tudo que tem embaixo dela até o próximo <li> de "Análises"
idx_rel = html.find('href="/relatorio_consolidado"')
if idx_rel != -1:
    # Encontra onde começa o <li> do Relatório
    start_li = html.rfind('<li', 0, idx_rel)
    # Encontra onde termina a tag <a> do Relatório
    end_a = html.find('</a>', idx_rel) + 4
    
    # Encontra onde começa o próximo item real (Análises Contábeis)
    idx_analises = html.find('Análises Contábeis', end_a)
    if idx_analises != -1:
        # Pega o <li> pai das Análises
        start_li_analises = html.rfind('<li', 0, idx_analises)
        
        # Bloco limpo: Apenas o link do relatório com estilo de topo
        bloco_limpo = '''
    <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>
'''
        # Substitui TUDO que estava no meio (o lixo criado) pelo bloco limpo
        html = html[:start_li] + bloco_limpo + html[start_li_analises:]
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Submenu indevido removido. O Relatório Consolidado agora é apenas um item de menu limpo.")
    else:
        print("[AVISO] Não achei o item 'Análises Contábeis' para servir de limite.")
else:
    print("[AVISO] Não achei o link do relatório consolidado no HTML.")
