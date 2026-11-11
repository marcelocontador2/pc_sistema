import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_menu_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona o link após o item 'Custo de Pessoal' na lista de links que o menu move
alvo = "'Custo de Pessoal'"
novo = "'Custo de Pessoal',\n        'Notas Explicativas'"

if 'Notas Explicativas' not in html:
    html = html.replace(alvo, novo, 1)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Link 'Notas Explicativas' adicionado ao menu.")
else:
    print("[AVISO] Link já existe no menu.")
