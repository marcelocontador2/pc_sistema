import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_cards_seguro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona os cards de índices após o card de despesa
alvo = '<div class="value" id="dash-despesa">R$ --</div>'
if alvo in html:
    # Localiza o fechamento da div do card e insere após o bloco de cards
    pos = html.find(alvo)
    if pos != -1:
        fim_card = html.find('</div>', pos) + 6
        fim_grid = html.find('</div>', fim_card) + 6
        
        cards_indices = '''
    <div class="dashboard-cards" style="margin-top: 20px;">
        <div class="dash-card" style="border-left-color: #28a745;">
            <h3>Liquidez Corrente</h3>
            <div class="value" id="dash-liq-corrente">--</div>
        </div>
        <div class="dash-card" style="border-left-color: #28a745;">
            <h3>Liquidez Imediata</h3>
            <div class="value" id="dash-liq-imediata">--</div>
        </div>
        <div class="dash-card" style="border-left-color: #ffc107;">
            <h3>Endividamento Geral</h3>
            <div class="value" id="dash-endividamento">--</div>
        </div>
        <div class="dash-card" style="border-left-color: #ffc107;">
            <h3>Imobilização do PL</h3>
            <div class="value" id="dash-imobilizacao">--</div>
        </div>
    </div>
'''
        html = html[:fim_grid] + cards_indices + html[fim_grid:]
        print("[OK] Cards de índices inseridos após os cards de totais.")

# 2. Atualiza o script do dashboard para preencher os índices (sem regex)
alvo_script = """document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);"""
novo_script = """document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);
                document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = liq.endividamento_geral ? liq.endividamento_geral + '%' : '--';
                document.getElementById('dash-imobilizacao').innerText = liq.imobilizacao_pl ? liq.imobilizacao_pl + '%' : '--';"""

if alvo_script in html:
    html = html.replace(alvo_script, novo_script)
    print("[OK] Script do dashboard atualizado para preencher os índices.")
else:
    print("[AVISO] Linha do script não encontrada. Verifique manualmente.")

# 3. Garante que a variável 'liq' está sendo capturada no script
alvo_liq = """const orc = data.encontrados.analise_orcamentaria?.dados?.atual || {};"""
novo_liq = """const orc = data.encontrados.analise_orcamentaria?.dados?.atual || {};
                const liq = data.encontrados.liquidez?.dados || {};"""

if alvo_liq in html:
    html = html.replace(alvo_liq, novo_liq)
    print("[OK] Variável 'liq' adicionada ao script.")
else:
    print("[AVISO] Linha da variável 'orc' não encontrada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html atualizado com sucesso.")
