import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a lista de links que o JS move (linksParaMover)
padrao = r"(const linksParaMover = \[.*?)(\];)"
match = re.search(padrao, html, re.DOTALL)

if match:
    lista_antiga = match.group(1)
    # Adiciona 'Notas Explicativas' após 'Custo de Pessoal'
    if 'Notas Explicativas' not in lista_antiga:
        lista_nova = lista_antiga.replace("'Custo de Pessoal'", "'Custo de Pessoal',\n        'Notas Explicativas'")
        html = html.replace(lista_antiga, lista_nova)
        with open(ARQ, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Link 'Notas Explicativas' adicionado à lista correta do menu.")
    else:
        print("[AVISO] Link já existe na lista.")
else:
    print("[ERRO] Lista 'linksParaMover' não encontrada.")
