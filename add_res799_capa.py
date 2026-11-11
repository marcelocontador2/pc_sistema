import shutil
from datetime import datetime

ARQ = r"pc_frontend\relatorio_consolidado_template.html"
backup = f"pc_frontend/relatorio_consolidado_template.html.bak_res799_capa_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Procura o trecho onde as normas estão listadas na capa
# Estratégia: procura "Resolução Cofen nº 814/2026" e adiciona a 799/2025 logo após
alvo = "Resolução Cofen nº 814/2026"
nova_norma = "Resolução Cofen nº 799/2025"

# Se a 799 ainda não estiver na capa, adiciona
if nova_norma not in html:
    # Tenta adicionar após a 814
    html = html.replace(
        alvo,
        f"{alvo} <span style='font-size:9px; color:#666; font-style:italic;'>(Limites de despesa com pessoal e governança corporativa.)</span> • {nova_norma} <span style='font-size:9px; color:#666; font-style:italic;'>(Estabelece diretrizes para a gestão de riscos e controles internos administrativos.)</span>",
        1
    )
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Resolução 799/2025 adicionada à capa do Relatório Consolidado.")
else:
    print("[AVISO] A Resolução 799/2025 já está na capa.")
