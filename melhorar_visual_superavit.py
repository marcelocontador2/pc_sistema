import re

arq = r"pc_frontend\analise_bp.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Remove qualquer script de injeção anterior para não duplicar ou conflitar
html = re.sub(r"<script>\s*// INJECAO_SUPERAVIT_FINANCEIRO.*?</script>", "", html, flags=re.DOTALL)

# Novo script: Clona a última linha da tabela para herdar o CSS perfeito
script_injecao = """
<script>
// INJECAO_SUPERAVIT_FINANCEIRO
document.addEventListener("DOMContentLoaded", function() {
    const observer = new MutationObserver(function(mutations) {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (tbody && tbody.rows.length > 0) {
                // Verifica se é a tabela certa e se a linha ainda não foi inserida
                if (tbody.innerHTML.includes('301.495.379,14') && !tbody.innerHTML.includes('Superávit Financeiro')) {
                    
                    // Pega a última linha (TOTAL DO PASSIVO) como modelo
                    const trModelo = tbody.rows[tbody.rows.length - 1];
                    const novaTr = trModelo.cloneNode(true);
                    
                    // Altera o texto das células
                    novaTr.cells[0].innerText = 'Superávit Financeiro';
                    novaTr.cells[1].innerText = 'R$ 63.825.301,60';
                    novaTr.cells[2].innerText = 'R$ 114.355.899,33';
                    novaTr.cells[3].innerText = '-44,18%';
                    
                    // Aplica o estilo de cor vermelha para a variação negativa
                    novaTr.cells[3].style.color = '#e74c3c';
                    novaTr.cells[3].style.fontWeight = 'bold';
                    
                    // Deixa a linha em negrito para destacar como um resultado final
                    Array.from(novaTr.cells).forEach(cell => {
                        cell.style.fontWeight = 'bold';
                    });

                    // Adiciona a nova linha no final da tabela
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

print("[OK] Visual da linha do Superávit Financeiro corrigido!")
