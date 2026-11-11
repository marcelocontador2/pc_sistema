import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_grid_4col_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Ajusta o CSS do grid para 4 colunas fixas (em vez de auto-fit)
css_antigo = """
    .dashboard-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
"""

css_novo = """
    .dashboard-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
    @media (max-width: 900px) { .dashboard-cards { grid-template-columns: repeat(2, 1fr); } }
"""

if css_antigo in html:
    html = html.replace(css_antigo, css_novo)
    print("[OK] CSS do grid ajustado para 4 colunas.")

# 2. Remove a margem-top do segundo bloco de cards (para ficar alinhado)
html = html.replace('<div class="dashboard-cards" style="margin-top: 20px;">', '<div class="dashboard-cards">')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Margem do segundo bloco removida.")
