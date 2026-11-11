import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_fix_js_notas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Encontra o bloco onde o JS insere o menu de Análises após o Relatório Consolidado
alvo = """    if (liConsolidado) {
        liConsolidado.parentElement.insertBefore(novoLi, liConsolidado.nextSibling);
    } else {
        menuPrincipal.appendChild(novoLi);
    }"""

novo = """    if (liConsolidado) {
        liConsolidado.parentElement.insertBefore(novoLi, liConsolidado.nextSibling);
        // Garante que o link 'Notas Explicativas' permaneça no menu principal
        const liNotas = Array.from(menuPrincipal.querySelectorAll('li')).find(li => li.textContent.includes('Notas Explicativas'));
        if (liNotas) {
            liConsolidado.parentElement.insertBefore(liNotas, liConsolidado.nextSibling);
        }
    } else {
        menuPrincipal.appendChild(novoLi);
    }"""

if alvo in html:
    html = html.replace(alvo, novo)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] JavaScript do menu corrigido para preservar o link 'Notas Explicativas'.")
else:
    print("[AVISO] Bloco do JavaScript não encontrado no formato esperado.")
    # Tenta uma abordagem mais flexível
    padrao = r'(liConsolidado\.parentElement\.insertBefore\(novoLi, liConsolidado\.nextSibling\);)'
    if re.search(padrao, html):
        html = re.sub(padrao, r'\1\n        const liNotas = Array.from(menuPrincipal.querySelectorAll(\'li\')).find(li => li.textContent.includes(\'Notas Explicativas\'));\n        if (liNotas) { liConsolidado.parentElement.insertBefore(liNotas, liConsolidado.nextSibling); }', html, count=1)
        with open(ARQ, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] JavaScript do menu corrigido (via regex).")
    else:
        print("[ERRO] Não foi possível encontrar o ponto de inserção no JavaScript.")
