import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_consolidado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Procura a tag <li> que contém "Análises Contábeis" (o título do submenu)
# e injeta o novo item "Relatório Consolidado" logo ANTES dele.
padrao = re.compile(r'(<li[^>]*>\s*<a[^>]*>\s*Análises Contábeis\s*</a>\s*</li>)', re.IGNORECASE)

match = padrao.search(html)
if match:
    bloco_analises = match.group(1)
    # Novo item: mesmo estilo visual dos outros links, mas com negrito (para ficar fora do submenu)
    novo_item = '''
    <li>
        <a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a>
    </li>
    '''
    # Insere o novo item antes do bloco de "Análises Contábeis"
    html = html.replace(bloco_analises, novo_item + "\n    " + bloco_analises, 1)
    
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Item 'Relatório Consolidado' injetado no HTML com sucesso.")
else:
    print("[AVISO] Não foi possível encontrar o bloco 'Análises Contábeis' no HTML para injetar o item.")

# =========================================================
# Cria a rota no Backend (se não existir) para não dar 404
# =========================================================
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

if "@app.get(\"/relatorio_consolidado\"" not in main_code:
    rota_fake = '''
@app.get("/relatorio_consolidado", response_class=HTMLResponse)
def relatorio_consolidado():
    return HTMLResponse(content="<html><body style='font-family: Arial; padding: 50px; text-align: center;'><h1>Relatório Consolidado</h1><p>Página em construção. Os relatórios serão exibidos aqui.</p><a href='/'>Voltar</a></body></html>")
'''
    # Insere a rota no final do arquivo main.py
    main_code += "\n" + rota_fake
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rota /relatorio_consolidado criada no backend.")
else:
    print("[INFO] Rota /relatorio_consolidado já existe no backend.")

print("\n=== PROXIMO PASSO ===")
print("1. Se o servidor não estiver rodando, suba ele.")
print("2. Va no navegador e aperte Ctrl+Shift+R.")
print("3. O menu 'Relatório Consolidado' deve aparecer logo acima de 'Análises Contábeis'.")
