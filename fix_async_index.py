import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_fix_async_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove qualquer "async" solto no script (que está causando o erro)
# Procura por linhas que tenham apenas "async" no início (fora de funções)
html = re.sub(r'^\s*async\s*$', '', html, flags=re.MULTILINE)

# 2. Garante que o link "Notas Explicativas" está no lugar certo
# Remove duplicatas se houver
html = re.sub(r'<a href="/notas_explicativas".*?</a>\s*<a href="/notas_explicativas".*?</a>', 
              '<a href="/notas_explicativas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Notas Explicativas</a>', html)

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html corrigido.")
