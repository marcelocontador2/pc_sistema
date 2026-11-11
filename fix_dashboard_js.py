import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\index.html"
backup = f"pc_frontend/index.html.bak_dash_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Remove o script antigo do dashboard (se existir)
padrao_script = r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{.*?\}\);\s*</script>'
html = re.sub(padrao_script, '', html, flags=re.DOTALL)

# Adiciona o script corrigido antes do </body>
script_corrigido = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/relatorio_consolidado/2026-TRIMESTRE-3')
        .then(r => r.json())
        .then(data => {
            console.log('Dados recebidos:', data);
            if (data.encontrados && data.encontrados.analise_bp) {
                const bp = data.encontrados.analise_bp.dados?.dados || {};
                const orc = data.encontrados.analise_orcamentaria?.dados?.atual || {};
                
                const fmt = (v) => {
                    if (v === undefined || v === null) return 'R$ --';
                    return 'R$ ' + Number(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                };
                
                document.getElementById('dash-ativo').innerText = fmt(bp.total_ativo?.atual);
                document.getElementById('dash-passivo').innerText = fmt(bp.total_passivo?.atual);
                document.getElementById('dash-receita').innerText = fmt(orc.receita_realizada);
                document.getElementById('dash-despesa').innerText = fmt(orc.despesa_empenhada);
            }
        })
        .catch(err => console.error('Erro ao carregar dashboard:', err));
});
</script>
"""

html = html.replace('</body>', script_corrigido + '</body>')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Script do dashboard corrigido.")
