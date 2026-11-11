import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_correto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona o link no HTML estático (linha 177)
alvo_html = '<a href="/analise_custo_pessoal" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Custo de Pessoal</a>'
novo_html = alvo_html + '\n        <a href="/notas_explicativas" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Notas Explicativas</a>'

if alvo_html in html and '/notas_explicativas' not in html:
    html = html.replace(alvo_html, novo_html, 1)
    print("[OK] Link adicionado ao HTML estático.")

# 2. Adiciona o link no JavaScript (ordemLinks)
alvo_js = "{ txt: 'Custo de Pessoal', href: '/analise_custo_pessoal' }"
novo_js = "{ txt: 'Custo de Pessoal', href: '/analise_custo_pessoal' },\n        { txt: 'Notas Explicativas', href: '/notas_explicativas' }"

if alvo_js in html and "'Notas Explicativas'" not in html.split("ordemLinks")[1][:500]:
    html = html.replace(alvo_js, novo_js, 1)
    print("[OK] Link adicionado ao JavaScript (ordemLinks).")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Arquivo index.html atualizado com sucesso.")
