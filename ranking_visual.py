arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Remove qualquer tentativa anterior de ranking ou nota que possa ter ficado no código
html = re.sub(r"// --- Tabela de Ranking \(Ordem Decrescente\) ---.*?H \+= tab\(\['#', 'Centro de Custo', 'Gasto Atual', 'Variação \(%\)'\], rowsRanking\);", "", html, flags=re.DOTALL)
html = re.sub(r"// --- Destaque Maior Gasto ---.*?H \+= '</div>';", "", html, flags=re.DOTALL)

# Cria o script JavaScript que fará a mágica no navegador
script_magico = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Espera um pouco para garantir que o relatório foi gerado na tela
    setTimeout(function() {
        // Procura o título "11. Análise por Centro de Custos"
        const titulos = Array.from(document.querySelectorAll('h2, h3, .titulo, .title'));
        const titulo11 = titulos.find(t => t.innerText.includes('11. Análise por Centro de Custos'));
        
        if (!titulo11) {
            console.log('Título da seção 11 não encontrado.');
            return;
        }

        // Encontra a tabela que vem logo após esse título
        let tabelaOriginal = null;
        let el = titulo11.nextElementSibling;
        while (el) {
            if (el.tagName === 'TABLE') {
                tabelaOriginal = el;
                break;
            }
            // Se a tabela estiver dentro de uma div
            const tabDentro = el.querySelector('table');
            if (tabDentro) {
                tabelaOriginal = tabDentro;
                break;
            }
            el = el.nextElementSibling;
        }

        if (!tabelaOriginal) {
            console.log('Tabela da seção 11 não encontrada.');
            return;
        }

        // Extrai as linhas da tabela (ignorando o cabeçalho e o TOTAL)
        const linhas = Array.from(tabelaOriginal.querySelectorAll('tbody tr'));
        const dados = [];
        
        linhas.forEach(tr => {
            const colunas = Array.from(tr.querySelectorAll('td'));
            if (colunas.length >= 4) {
                const nome = colunas[0].innerText.trim();
                const valorStr = colunas[1].innerText.trim();
                const variacaoStr = colunas[3].innerText.trim();
                
                // Ignora a linha TOTAL
                if (nome.toUpperCase().includes('TOTAL')) return;
                
                // Converte "R$ 16.937.035,31" para float
                const valorNum = parseFloat(valorStr.replace('R$', '').replace(/\\./g, '').replace(',', '.').trim()) || 0;
                
                dados.push({ nome, valorStr, valorNum, variacaoStr });
            }
        });

        if (dados.length === 0) {
            console.log('Nenhum dado encontrado para o ranking.');
            return;
        }

        // Ordena do maior para o menor
        dados.sort((a, b) => b.valorNum - a.valorNum);

        // Cria a nova tabela HTML
        let htmlRanking = '<h3 style="color:#0a2b5c; margin-top:20px; font-size:14px;">Ranking de Gastos (Maior para Menor)</h3>';
        htmlRanking += '<table style="width:100%; border-collapse: collapse; font-size: 11px; margin-top: 10px;">';
        htmlRanking += '<thead><tr style="background:#0a2b5c; color:#fff;">';
        htmlRanking += '<th style="padding:8px; border:1px solid #ccc; text-align:left;">#</th>';
        htmlRanking += '<th style="padding:8px; border:1px solid #ccc; text-align:left;">Centro de Custo</th>';
        htmlRanking += '<th style="padding:8px; border:1px solid #ccc; text-align:right;">Gasto Atual</th>';
        htmlRanking += '<th style="padding:8px; border:1px solid #ccc; text-align:right;">Variação (%)</th>';
        htmlRanking += '</tr></thead><tbody>';

        dados.forEach((d, i) => {
            const bg = i % 2 === 0 ? '#f8f9fa' : '#fff';
            htmlRanking += `<tr style="background:${bg}; border-bottom:1px solid #ddd;">`;
            htmlRanking += `<td style="padding:8px; border:1px solid #ccc;"><b>${i + 1}</b></td>`;
            htmlRanking += `<td style="padding:8px; border:1px solid #ccc;">${d.nome}</td>`;
            htmlRanking += `<td style="padding:8px; border:1px solid #ccc; text-align:right;">${d.valorStr}</td>`;
            htmlRanking += `<td style="padding:8px; border:1px solid #ccc; text-align:right;">${d.variacaoStr}</td>`;
            htmlRanking += '</tr>';
        });

        htmlRanking += '</tbody></table>';

        // Insere a nova tabela logo após a tabela original
        tabelaOriginal.insertAdjacentHTML('afterend', htmlRanking);
        console.log('Tabela de ranking inserida com sucesso!');
    }, 500); // 500ms de delay para garantir que o relatório carregou
});
</script>
"""

# Injeta o script antes do fechamento da tag </body>
if '</body>' in html:
    html = html.replace('</body>', script_magico + '\n</body>')
    print("[OK] Script de ranking visual injetado no final do HTML.")
else:
    print("[ERRO] Tag </body> não encontrada.")

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)
