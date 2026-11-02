c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# 1. Adiciona o plugin datalabels no head (junto com o Chart.js)
if "chartjs-plugin-datalabels" not in c:
    c = c.replace(
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>'
    )

# 2. Substitui o bloco do gráfico de donut para incluir o datalabels
antigo_donut = """                // 2. Gráfico de Donut
                const centros = d.atual.centros.sort((a, b) => b.valor - a.valor);
                const labels = centros.map(c => c.nome.length > 25 ? c.nome.substring(0, 25) + '...' : c.nome);
                const dataValores = centros.map(c => c.valor);
                const cores = ['#0a1c3a', '#1a3b5c', '#2c5282', '#5b8fc9', '#a0c4e8', '#d0e2f2'];
                
                const ctxDonut = document.getElementById('grafico-donut').getContext('2d');
                new Chart(ctxDonut, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: dataValores,
                            backgroundColor: cores,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });"""

novo_donut = """                // 2. Gráfico de Donut com rótulos
                const centros = d.atual.centros.sort((a, b) => b.valor - a.valor);
                const totalGeral = d.atual.total;
                
                // Extrai apenas o código do centro (ex: "05 - AF 05 Coor..." -> "AF 05")
                const labelsCurto = centros.map(c => {
                    const match = c.nome.match(/AF\\s*\\d+/i);
                    return match ? match[0].toUpperCase() : c.nome.substring(0, 15);
                });
                const dataValores = centros.map(c => c.valor);
                const percentuais = centros.map(c => totalGeral > 0 ? (c.valor / totalGeral * 100) : 0);
                const cores = ['#0a1c3a', '#1a3b5c', '#2c5282', '#5b8fc9', '#a0c4e8', '#d0e2f2'];
                
                const ctxDonut = document.getElementById('grafico-donut').getContext('2d');
                new Chart(ctxDonut, {
                    type: 'doughnut',
                    data: {
                        labels: labelsCurto,
                        datasets: [{
                            data: dataValores,
                            backgroundColor: cores,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                color: '#fff',
                                font: { weight: 'bold', size: 11 },
                                formatter: function(value, context) {
                                    const idx = context.dataIndex;
                                    return labelsCurto[idx] + '\\n' + percentuais[idx].toFixed(2) + '%';
                                }
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });"""

if antigo_donut in c:
    c = c.replace(antigo_donut, novo_donut)
    print("[OK] Gráfico de donut atualizado com rótulos!")
else:
    print("[AVISO] Bloco do donut não encontrado. Tentando substituição flexível...")
    import re
    padrao = r'// 2\. Gráfico de Donut.*?new Chart\(ctxDonut, \{.*?\}\);'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, novo_donut, c, flags=re.DOTALL)
        print("[OK] Gráfico de donut substituído via regex!")

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado!")
