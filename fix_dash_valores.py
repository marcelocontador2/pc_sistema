import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_dash_valores_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Localiza o bloco do script do dashboard
alvo = """const bp = data.encontrados.analise_bp.dados?.dados || {};"""
novo = """const bp = data.encontrados.analise_bp?.dados?.dados || {};"""

if alvo in html:
    html = html.replace(alvo, novo)
    print("[OK] Caminho do BP corrigido (com optional chaining).")

# 2. Corrige o caminho do 'liq' (liquidez)
alvo_liq = """const liq = data.encontrados.liquidez?.dados || {};"""
novo_liq = """const liq = data.encontrados.liquidez?.dados?.liquidez || data.encontrados.liquidez?.dados || {};"""

if alvo_liq in html:
    html = html.replace(alvo_liq, novo_liq)
    print("[OK] Caminho do 'liq' corrigido.")

# 3. Garante que os valores dos índices sejam puxados corretamente
alvo_indices = """document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = liq.endividamento_geral ? liq.endividamento_geral + '%' : '--';
                document.getElementById('dash-imobilizacao').innerText = liq.imobilizacao_pl ? liq.imobilizacao_pl + '%' : '--';"""

novo_indices = """document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = liq.endividamento_geral ? liq.endividamento_geral + '%' : '--';
                document.getElementById('dash-imobilizacao').innerText = liq.imobilizacao_pl ? liq.imobilizacao_pl + '%' : '--';"""

if alvo_indices in html:
    html = html.replace(alvo_indices, novo_indices)
    print("[OK] Script dos índices ajustado (se necessário).")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Script atualizado.")
