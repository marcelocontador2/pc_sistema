import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_menu_definitivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove qualquer CSS de ordenação anterior
html = re.sub(r'<style>\s*/\* Força a ordem no menu principal \*/.*?</style>', '', html, flags=re.DOTALL)
html = re.sub(r'<style>\s*ul \{ display: flex; flex-direction: column; \}.*?</style>', '', html, flags=re.DOTALL)

# 2. Localiza o bloco de menus principais e reescreve na ordem correta
# O menu fica dentro de <aside class="sidebar">, na <ul> principal
padrao_menu = r'(<ul style="padding-left: 60px; margin-left: 0; list-style: none;">\s*)(.*?)(\s*</ul>)'
match = re.search(padrao_menu, html, re.DOTALL)

if match:
    # Monta o novo menu na ordem: Importar, Base Legal, Configuracoes, Relatorio Consolidado, Notas Explicativas
    novo_menu = '''
        <li><a href="#" id="menu-upload" onclick="mostrarTela('upload')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar Relatórios</a></li>
        <li><a href="/base_legal" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Base Legal</a></li>
        <li><a href="/configuracoes" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Configuracoes</a></li>
        <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>
        <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>
    '''
    html = html.replace(match.group(0), match.group(1) + novo_menu + match.group(3))
    print("[OK] Menu principal reescrito na ordem correta.")
else:
    print("[AVISO] Bloco do menu principal não encontrado.")

# 3. Remove o link "Notas Explicativas" de qualquer outro lugar (para não duplicar)
html = re.sub(r'<a href="/notas_explicativas".*?</a>', '', html)
# Reinsere o link apenas no lugar correto (já feito acima)
alvo_relatorio = '<a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a>'
if alvo_relatorio in html:
    html = html.replace(alvo_relatorio, alvo_relatorio + '\n        <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>', 1)

# 4. Ajusta o JavaScript que monta o submenu (para não mexer no "Notas Explicativas")
# Remove a lógica que insere o submenu "Análises Contábeis" e a recria
padrao_js = r'(// 4\. Insere o menu de Análises.*?)(?=\n\s*//|\n\s*function|\n\s*document)'
match_js = re.search(padrao_js, html, re.DOTALL)

if match_js:
    novo_js = '''
    // 4. Insere o menu de Análises APÓS o link de Notas Explicativas
    const liNotas = Array.from(menuPrincipal.querySelectorAll('li')).find(li => li.textContent.includes('Notas Explicativas'));
    const liConsolidado = Array.from(menuPrincipal.querySelectorAll('li')).find(li => li.textContent.includes('Relatório Consolidado'));
    
    if (liNotas) {
        liNotas.parentElement.insertBefore(novoLi, liNotas.nextSibling);
    } else if (liConsolidado) {
        liConsolidado.parentElement.insertBefore(novoLi, liConsolidado.nextSibling);
    } else {
        menuPrincipal.appendChild(novoLi);
    }
    '''
    html = html.replace(match_js.group(1), novo_js)
    print("[OK] JavaScript de inserção do submenu ajustado.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html atualizado.")
