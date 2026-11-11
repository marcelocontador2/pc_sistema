import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_cards_indices_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona o bloco de cards de índices após os cards de totais
cards_indices = """
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
"""

# Insere os cards após o bloco de cards de totais (que termina com </div> após "Despesa Empenhada")
alvo = '<div class="value" id="dash-despesa">R$ --</div>\n        </div>\n    </div>'
if alvo in html:
    html = html.replace(alvo, alvo + cards_indices, 1)
    print("[OK] Cards de índices adicionados.")
else:
    # Fallback: adiciona após o fechamento do primeiro dashboard-cards
    match = re.search(r'(<div class="dashboard-cards">.*?</div>\s*</div>)', html, re.DOTALL)
    if match:
        html = html.replace(match.group(1), match.group(1) + cards_indices, 1)
        print("[OK] Cards de índices adicionados (fallback).")
    else:
        print("[AVISO] Bloco de cards não encontrado.")

# 2. Atualiza o script para preencher os novos cards
script_novo = """
document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/relatorio_consolidado/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            if (data.encontrados && data.encontrados.analise_bp) {
                const bp = data.encontrados.analise_bp.dados?.dados || {};
                const orc = data.encontrados.analise_orcamentaria?.dados?.atual || {};
                const liq = data.encontrados.liquidez?.dados || {};
                
                const fmt = (v) => {
                    if (v === undefined || v === null) return 'R$ --';
                    return 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                };
                
                const fmtPct = (v) => {
                    if (v === undefined || v === null) return '--';
                    return Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
                };
                
                // Totais
                document.getElementById('dash-ativo').innerText = fmt(bp.total_ativo?.atual);
                document.getElementById('dash-passivo').innerText = fmt(bp.total_passivo?.atual);
                document.getElementById('dash-receita').innerText = fmt(orc.receita_realizada);
                document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);
                
                // Índices
                document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
                document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
                document.getElementById('dash-endividamento').innerText = fmtPct(liq.endividamento_geral);
                document.getElementById('dash-imobilizacao').innerText = fmtPct(liq.imobilizacao_pl);
            }
        })
        .catch(err => console.error('Erro ao carregar dashboard:', err));
});
"""

# Substitui o script antigo pelo novo
html = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{.*?\}\);\s*</script>', script_novo, html, flags=re.DOTALL)

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Script atualizado para preencher os índices.")
