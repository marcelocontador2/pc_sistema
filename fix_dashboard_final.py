import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_dash_limpo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove QUALQUER script de dashboard existente (para limpar o que quebrou)
padrao_script = r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{.*?\}\);\s*</script>'
html = re.sub(padrao_script, '', html, flags=re.DOTALL)

# 2. Adiciona o script correto e limpo antes do </body>
novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/relatorio_consolidado/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            // Dados do Balanço Patrimonial
            const bp = data.encontrados?.analise_bp?.dados?.dados || {};
            // Dados Orçamentários
            const orc = data.encontrados?.analise_orcamentaria?.dados?.atual || {};
            // Dados de Liquidez
            const liq_raw = data.encontrados?.liquidez?.dados || {};
            const liq = liq_raw.liquidez || {};
            const est = liq_raw.estrutura || {};

            // Função para formatar moeda
            const fmt = (v) => {
                if (v === undefined || v === null) return 'R$ --';
                return 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            };

            // Função para formatar percentual
            const fmtPct = (v) => {
                if (v === undefined || v === null) return '--';
                return v + '%';
            };

            // Preenche os cards de totais
            document.getElementById('dash-ativo').innerText = fmt(bp.total_ativo?.atual);
            document.getElementById('dash-superavit').innerText = fmt(bp.superavit_financeiro?.atual);
            document.getElementById('dash-receita').innerText = fmt(orc.receita_realizada);
            document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);

            // Preenche os cards de índices
            document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
            document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
            document.getElementById('dash-endividamento').innerText = fmtPct(est.endividamento_geral);
            document.getElementById('dash-imobilizacao').innerText = fmtPct(est.imobilizacao_pl);
        })
        .catch(err => {
            console.error('Erro ao carregar dashboard:', err);
            // Fallback: mostra aviso se a API falhar
            ['dash-ativo', 'dash-superavit', 'dash-receita', 'dash-despesa'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.innerText = 'Erro';
            });
        });
});
</script>
"""

html = html.replace('</body>', novo_script + '</body>')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Script do dashboard reescrito e limpo.")
