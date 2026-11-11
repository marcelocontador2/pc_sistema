import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove o link "Notas Explicativas" de qualquer lugar onde ele esteja
html = re.sub(r'<li><a href="/notas_explicativas".*?</li>', '', html, flags=re.DOTALL)
html = re.sub(r'<a href="/notas_explicativas".*?</a>', '', html, flags=re.DOTALL)

# 2. Adiciona o link como item principal, logo após o <li> do Relatório Consolidado
alvo = '<li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>'

if alvo in html:
    novo = alvo + '\n    <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>'
    html = html.replace(alvo, novo, 1)
    print("[OK] Link 'Notas Explicativas' inserido como item principal após 'Relatório Consolidado'.")
else:
    print("[ERRO] Link do Relatório Consolidado não encontrado.")

# 3. Remove qualquer código JavaScript que tente mover o link
html = re.sub(r'// Garante que o link.*?\n\s*if \(liNotas\) \{.*?\n\s*\}', '', html, flags=re.DOTALL)

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html corrigido e link posicionado corretamente.")
