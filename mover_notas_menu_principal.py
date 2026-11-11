import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_notas_principal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove o link do submenu (dentro de <ul> de Análises)
html = re.sub(r'<a href="/notas_explicativas".*?</a>', '', html, flags=re.DOTALL)

# 2. Adiciona o link como item principal, logo após "Relatório Consolidado"
# Procura o <li> que contém o link do Relatório Consolidado
alvo = '<li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>'
novo = alvo + '\n    <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>'

if alvo in html:
    html = html.replace(alvo, novo, 1)
    print("[OK] Link 'Notas Explicativas' movido para o menu principal (após Relatório Consolidado).")
else:
    print("[AVISO] Link do Relatório Consolidado não encontrado no formato esperado.")
    # Tentativa alternativa: procurar o <li> do Relatório Consolidado
    padrao = r'(<li[^>]*>\s*<a[^>]*href="/relatorio_consolidado"[^>]*>.*?</a>\s*</li>)'
    match = re.search(padrao, html, re.DOTALL)
    if match:
        html = html.replace(match.group(1), match.group(1) + '\n    <li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Notas Explicativas</a></li>', 1)
        print("[OK] Link adicionado ao menu principal (tentativa alternativa).")
    else:
        print("[ERRO] Não foi possível encontrar o Relatório Consolidado no menu.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html atualizado.")
