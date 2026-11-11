import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_superavit_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza o script do dashboard
padrao = r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{.*?\}\);\s*</script>'
match = re.search(padrao, html, re.DOTALL)

if match:
    # Novo script: busca os dados do consolidado E da API do BP (para o superávit)
    novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // 1. Busca os dados do relatório consolidado (para os totais e índices)
    fetch('/api/relatorio_consolidado/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            const bp = data.encontrados?.analise_bp?.dados?.dados || {};
            const orc = data.encontrados?.analise_orcamentaria?.dados?.atual || {};
            const liq_raw = data.encontrados?.liquidez?.dados || {};
            const liq = liq_raw.liquidez || {};
            const est = liq_raw.estrutura || {};

            const fmt = (v) => {
                if (v === undefined || v === null) return 'R$ --';
                return 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            };
            const fmtPct = (v) => {
                if (v === undefined || v === null) return '--';
                return v + '%';
            };

            // Totais
            document.getElementById('dash-ativo').innerText = fmt(bp.total_ativo?.atual);
            document.getElementById('dash-receita').innerText = fmt(orc.receita_realizada);
            document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);

            // Índices
            document.getElementById('dash-liq-corrente').innerText = liq.liquidez_corrente || '--';
            document.getElementById('dash-liq-imediata').innerText = liq.liquidez_imediata || '--';
            document.getElementById('dash-endividamento').innerText = fmtPct(est.endividamento_geral);
            document.getElementById('dash-imobilizacao').innerText = fmtPct(est.imobilizacao_pl);
        })
        .catch(err => console.error('Erro ao carregar consolidado:', err));

    // 2. Busca o Superávit Financeiro diretamente da API do BP
    fetch('/api/analise_bp/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            const bp = data.dados?.dados || data.dados || {};
            const superavit = bp.superavit_financeiro?.atual || 0;
            const fmt = (v) => {
                if (v === undefined || v === null || v === 0) return 'R$ --';
                return 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            };
            document.getElementById('dash-superavit').innerText = fmt(superavit);
        })
        .catch(err => console.error('Erro ao carregar superávit:', err));
});
</script>
"""
    html = html.replace(match.group(0), novo_script)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Script do dashboard atualizado para buscar superávit da API do BP.")
else:
    print("[ERRO] Script do dashboard não encontrado.")
