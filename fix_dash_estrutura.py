import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_dash_estrutura_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Corrige o caminho para buscar a estrutura (endividamento e imobilização)
alvo = """const liq = data.encontrados.liquidez?.dados?.liquidez || data.encontrados.liquidez?.dados || {};"""
novo = """const liq_raw = data.encontrados.liquidez?.dados || {};
                const liq = liq_raw.liquidez || {};
                const est = liq_raw.estrutura || {};"""

if alvo in html:
    html = html.replace(alvo, novo)
    print("[OK] Variáveis de liquidez e estrutura separadas.")

# 2. Atualiza os cards de endividamento e imobilização para usar 'est'
alvo_indices = """document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = liq.endividamento_geral ? liq.endividamento_geral + '%' : '--';
                document.getElementById('dash-imobilizacao').innerText = liq.imobilizacao_pl ? liq.imobilizacao_pl + '%' : '--';"""

novo_indices = """document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = est.endividamento_geral ? est.endividamento_geral + '%' : '--';
                document.getElementById('dash-imobilizacao').innerText = est.imobilizacao_pl ? est.imobilizacao_pl + '%' : '--';"""

if alvo_indices in html:
    html = html.replace(alvo_indices, novo_indices)
    print("[OK] Cards de estrutura corrigidos.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Script atualizado.")
