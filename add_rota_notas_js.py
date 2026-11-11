import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_rota_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Procura a lista "ordemLinks" (que tem os hrefs)
padrao = r"({ txt: 'Custo de Pessoal', href: '/analise_custo_pessoal' })"
novo = "{ txt: 'Custo de Pessoal', href: '/analise_custo_pessoal' },\n        { txt: 'Notas Explicativas', href: '/notas_explicativas' }"

if '/notas_explicativas' not in html:
    html = html.replace(padrao, novo)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Rota /notas_explicativas adicionada ao JavaScript do menu.")
else:
    print("[AVISO] Rota já existe no JavaScript.")
