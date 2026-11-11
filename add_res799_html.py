import shutil
from datetime import datetime

ARQ = r"pc_frontend\base_legal.html"
backup = f"pc_frontend/base_legal.html.bak_res799_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Procura a linha da Resolução 814/2026 e adiciona a 799/2025 logo abaixo
alvo = "Resolução Cofen nº 814/2026"
nova_linha = "Resolução Cofen nº 799/2025"

# Se a 799 já não estiver no HTML, adiciona
if nova_linha not in html:
    # Tenta inserir após a primeira ocorrência da 814
    html = html.replace(alvo, alvo + f"<li>{nova_linha}</li>", 1)
    
    # Se não funcionar (por causa de tags), tenta um replace mais simples
    if nova_linha not in html:
        html = html.replace("<li>Resolução Cofen nº 814/2026</li>", 
                           "<li>Resolução Cofen nº 814/2026</li>\n<li>Resolução Cofen nº 799/2025</li>")
        
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Resolução 799/2025 adicionada ao HTML.")
else:
    print("[AVISO] A Resolução 799/2025 já está no HTML.")
