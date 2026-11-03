c = open('relatorio_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Aumentar legendas do gráfico de ranking (eixo Y e X)
# No Chart.js, o tamanho dos ticks é controlado por 'font: { size: X }'
c = c.replace(
    "y: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 } } }",
    "y: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 14 } } }"
)
c = c.replace(
    "x: { beginAtZero: true, grid: { color: '#edf2f7' }, ticks: { font: { family: 'Inter', size: 10 } } }",
    "x: { beginAtZero: true, grid: { color: '#edf2f7' }, ticks: { font: { family: 'Inter', size: 12 } } }"
)

# 2. Aumentar legenda do gráfico de grupos (eixo X)
c = c.replace(
    "x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 9 } } }",
    "x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 13 } } }"
)

# 3. Aumentar o tamanho dos percentuais no donut (datalabels)
c = c.replace(
    "datalabels: { color: '#fff', font: { weight: 'bold', size: 11 }, formatter: (v, ctx) => ((v/totalCores)*100).toFixed(1) + '%' }",
    "datalabels: { color: '#fff', font: { weight: 'bold', size: 16 }, formatter: (v, ctx) => ((v/totalCores)*100).toFixed(1) + '%' }"
)

open('relatorio_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Tamanhos das legendas e percentuais aumentados!")
