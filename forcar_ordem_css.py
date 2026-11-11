import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_ordem_css_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove qualquer tentativa anterior de mover o item no HTML
# (se existir, para não duplicar)
html = re.sub(r'<li><a href="/notas_explicativas".*?</li>', '', html, flags=re.DOTALL)

# 2. Adiciona um CSS que força a ordem no menu principal
css_ordem = """
<style>
/* Força a ordem no menu principal */
ul li:nth-child(4) { order: 1; } /* Relatório Consolidado */
ul li:nth-child(5) { order: 2; } /* Notas Explicativas */
/* Opcional: ajusta o layout para garantir que o order funcione */
ul { display: flex; flex-direction: column; }
</style>
"""

if 'Força a ordem no menu principal' not in html:
    html = html.replace('</head>', css_ordem + '</head>')
    print("[OK] CSS de ordenação adicionado.")
else:
    print("[AVISO] CSS já existe.")

# 3. Garante que o link está no HTML estático
alvo_html = '<li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>'
if alvo_html in html and 'notas_explicativas' not in html:
    novo_html = alvo_html + '\n    <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>'
    html = html.replace(alvo_html, novo_html, 1)
    print("[OK] Link estático adicionado.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Index atualizado com ordem forçada via CSS.")
