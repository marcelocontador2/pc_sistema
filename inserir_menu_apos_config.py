import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Procurar a tag <li> do item "Configuracoes" (sem acento, como está no arquivo)
padrao = re.compile(
    r'(<li><a href="/configuracoes"[^>]*>Configuracoes</a></li>)',
    re.IGNORECASE
)

match = padrao.search(html)

if match:
    bloco_config = match.group(1)
    
    # Novo item no mesmo estilo, logo após Configuracoes
    novo_item = '''
    <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>'''
    
    html = html.replace(bloco_config, bloco_config + novo_item, 1)
    
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Link 'Relatório Consolidado' inserido após 'Configuracoes' no HTML estático.")
    print("[OK] Menu 'Análises Contábeis' (dinâmico) NÃO foi tocado, então ele continua funcionando.")
else:
    print("[ERRO] Não encontrei o <li> de 'Configuracoes' para inserir o novo item.")
