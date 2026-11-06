import re

arq = r"pc_frontend\analise_bp.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Se o script já foi injetado antes, não faz nada para não duplicar
if "// INJECAO_SUPERAVIT_FINANCEIRO" in html:
    print("[AVISO] O script já está no arquivo. Nada a fazer.")
    raise SystemExit

# Script seguro que espera a tabela renderizar e adiciona a linha
script_injecao = """
<script>
// INJECAO_SUPERAVIT_FINANCEIRO
document.addEventListener("DOMContentLoaded", function() {
    const observer = new MutationObserver(function(mutations) {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (tbody) {
                // Verifica se a tabela é a do Balanço Patrimonial (procurando o Ativo Circulante de Q3)
                if (tbody.innerHTML.includes('301.495.379,14') && !tbody.innerHTML.includes('Superávit Financeiro')) {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: left;">Superávit Financeiro</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">R$ 63.825.301,60</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">R$ 114.355.899,33</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #e74c3c; font-weight: bold;">-44,18%</td>
                    `;
                    tbody.appendChild(tr);
                }
            }
        });
    });
    // Fica observando o DOM até a tabela aparecer
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
</body>
"""

# Substitui o fechamento do body pelo script + fechamento do body
html = html.replace('</body>', script_injecao)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Script de injeção segura adicionado ao analise_bp.html!")
