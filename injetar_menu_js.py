import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_js_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Procura o script que monta o menu dinamicamente.
# Ele termina com algo como: submenu.appendChild(liConferencia); ... })
# Vamos adicionar uma nova linha no final desse bloco.
idx_script = html.rfind('linkPai.addEventListener("click", function()')
if idx_script != -1:
    # Encontra o fim desse event listener
    end_script = html.find('});', idx_script)
    if end_script != -1:
        end_script += 3
        
        # Insere o código para criar o novo link no MENU PRINCIPAL (fora do submenu)
        novo_codigo = """
        // --- INJETADO: RELATORIO CONSOLIDADO ---
        const linkConsolidado = document.createElement('a');
        linkConsolidado.href = '/relatorio_consolidado';
        linkConsolidado.textContent = 'Relatório Consolidado';
        linkConsolidado.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
        
        const liConsolidado = document.createElement('li');
        liConsolidado.appendChild(linkConsolidado);
        
        // Insere o novo item logo APÓS o elemento <ul> do menu principal
        const menuPrincipal = document.querySelector('ul');
        if (menuPrincipal) {
            menuPrincipal.appendChild(liConsolidado);
        }
        // ------------------------------------------
"""
        html = html[:end_script] + novo_codigo + html[end_script:]
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Script JavaScript modificado com sucesso.")
    else:
        print("[ERRO] Não encontrei o fechamento do bloco de script.")
else:
    print("[AVISO] Não encontrei o trecho 'linkPai.addEventListener' no arquivo.")
