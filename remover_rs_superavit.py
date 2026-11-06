import re

arq = r"pc_frontend\analise_bp.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Remove o script antigo
html = re.sub(r"<script>\s*// INJECAO_SUPERAVIT_FINANCEIRO.*?</script>", "", html, flags=re.DOTALL)

# Novo script sem o R$
script_injecao = """
<script>
// INJECAO_SUPERAVIT_FINANCEIRO
document.addEventListener("DOMContentLoaded", function() {
    const observer = new MutationObserver(function(mutations) {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (tbody && tbody.rows.length > 0) {
                if (tbody.innerHTML.includes('301.495.379,14') && !tbody.innerHTML.includes('Superávit Financeiro')) {
                    
                    const trModelo = tbody.rows[tbody.rows.length - 1];
                    const novaTr = trModelo.cloneNode(true);
                    
                    novaTr.cells[0].innerText = 'Superávit Financeiro';
                    novaTr.cells[1].innerText = '63.825.301,60';
                    novaTr.cells[2].innerText = '114.355.899,33';
                    novaTr.cells[3].innerText = '-44,18%';
                    
                    novaTr.cells[3].style.color = '#e74c3c';
                    novaTr.cells[3].style.fontWeight = 'bold';
                    
                    Array.from(novaTr.cells).forEach(cell => {
                        cell.style.fontWeight = 'bold';
                    });

                    tbody.appendChild(novaTr);
                }
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
</body>
"""

html = html.replace('</body>', script_injecao)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Símbolo R$ removido do Superávit Financeiro!")
