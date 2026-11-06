import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_menu_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# =========================================================
# 1. INJETAR O ITEM "RELATÓRIO CONSOLIDADO" NO SCRIPT DINÂMICO
# =========================================================
# O script está criando os itens dentro do "submenu-analises".
# Vamos procurar a linha onde ele insere o primeiro item e colocar o nosso antes.

padrao_script = re.compile(r'(linkPai\.addEventListener\(\'click\', function\(\)\s*\{.*?)(submenu\.appendChild\(|const linkConf)', re.DOTALL)

# Vou usar a técnica do "âncora": procurar onde ele cria o 'linkConf' (Conferência) e injetar o nosso antes.
idx_conf = html.find("Conferência das Demonstrações")
if idx_conf != -1:
    # Encontra a tag <a> ou <li> que envolve isso e injeta o novo antes
    # Vamos procurar a definição do link da conferência para clonar
    # O script provavelmente faz algo como:
    # const linkConf = document.createElement('a'); linkConf.href = '/conferencia'; ...
    
    # Vou injetar um item logo antes do "Conferência" se ele estiver no JS
    # Procurar o trecho 'linkConf'
    idx_js = html.find("linkConf")
    if idx_js == -1:
        # Procura o texto 'Conferência' dentro de aspas (provável JS)
        idx_js = html.find("'Conferência das Demonstrações'")
        if idx_js == -1:
            idx_js = html.find('"Conferência das Demonstrações"')

    if idx_js != -1:
        # Vamos montar o bloco JS do novo link
        novo_js = """
    // --- NOVO MENU: RELATORIO CONSOLIDADO ---
    const linkConsolidado = document.createElement('a');
    linkConsolidado.href = '/relatorio_consolidado';
    linkConsolidado.textContent = 'Relatório Consolidado';
    linkConsolidado.style.cssText = 'display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;';
    const liConsolidado = document.createElement('li');
    liConsolidado.appendChild(linkConsolidado);
    submenu.appendChild(liConsolidado);
    // ----------------------------------------
"""
        # Insere o JS antes do trecho da conferência
        html = html[:idx_js] + novo_js + html[idx_js:]
        print("[OK] Menu 'Relatório Consolidado' injetado no script dinâmico.")
    else:
        print("[AVISO] Não encontrei o script da 'Conferência' para injetar.")
else:
    print("[AVISO] Não encontrei o texto 'Conferência das Demonstrações' no arquivo.")

# =========================================================
# 2. CRIAR A ROTA DO BACKEND (se não existir)
# =========================================================
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

if "/relatorio_consolidado" not in main_code:
    # Vou adicionar uma rota fake (por enquanto) que exibe "Em construção"
    rota_fake = '''
@app.get("/relatorio_consolidado", response_class=HTMLResponse)
def relatorio_consolidado():
    return HTMLResponse(content="<html><body style='font-family: Arial; padding: 50px; text-align: center;'><h1>Relatório Consolidado</h1><p>Em construção.</p><a href='/'>Voltar</a></body></html>")
'''
    # Adiciona logo após a rota /analises (ou no final do arquivo)
    idx_analises = main_code.find('def analises_em_breve')
    if idx_analises != -1:
        # Encontra o final da função (próxima @app)
        end_func = main_code.find("\n@app.", idx_analises)
        if end_func == -1:
            end_func = len(main_code)
        main_code = main_code[:end_func] + rota_fake + main_code[end_func:]
        print("[OK] Rota /relatorio_consolidado criada no backend (placeholder).")
    else:
        main_code += rota_fake
        print("[OK] Rota /relatorio_consolidado adicionada no final do main.py.")
else:
    print("[INFO] Rota /relatorio_consolidado já existe no backend.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PRÓXIMO PASSO ===")
print("1. REINICIE O SERVIDOR (Ctrl+C e suba de novo).")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. O item 'Relatório Consolidado' deve aparecer no menu lateral.")
