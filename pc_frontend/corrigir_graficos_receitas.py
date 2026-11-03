import re

c = open('relatorio_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Corrige o gráfico de grupos (rótulos "2025" -> "Período Anterior", "2026" -> "Período Atual")
# E troca a ordem: Período Atual primeiro, depois Anterior
c = c.replace(
    "{ label: '2025', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 }",
    "{ label: 'Período Anterior', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 }"
)
c = c.replace(
    "{ label: '2026', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 }",
    "{ label: 'Período Atual', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 }"
)

# Reordena os datasets (Atual primeiro)
c = c.replace(
    """                        datasets: [
                            { label: 'Período Anterior', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 },
                            { label: 'Período Atual', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 }
                        ]""",
    """                        datasets: [
                            { label: 'Período Atual', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: 'Período Anterior', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]"""
)

# 2. Corrige o gráfico de ranking para incluir comparativo (Atual + Anterior)
# Pega o bloco do gráfico de ranking e substitui por uma versão com dois datasets
padrao_ranking = r"new Chart\(document\.getElementById\('grafico-ranking'\)\.getContext\('2d'\), \{.*?\}\);"
novo_ranking = """new Chart(document.getElementById('grafico-ranking').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: coresAt.map(c => c.nome),
                        datasets: [
                            { label: 'Período Atual', data: coresAt.map(c => c.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: 'Período Anterior', data: coresAt.map(c => {
                                const anC = (an.cores || []).find(x => x.nome === c.nome);
                                return anC ? anC.realizado / 1000000 : 0;
                            }), backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        plugins: { 
                            legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8, font: { family: 'Inter', size: 11 } } },
                            tooltip: { callbacks: { label: function(ctx) { return ctx.dataset.label + ': R$ ' + ctx.raw.toFixed(2) + ' mi'; } } }
                        },
                        scales: { x: { beginAtZero: true, grid: { color: '#edf2f7' }, ticks: { font: { family: 'Inter', size: 10 } } }, y: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 } } } }
                    }
                });"""

if re.search(padrao_ranking, c, re.DOTALL):
    c = re.sub(padrao_ranking, novo_ranking, c, flags=re.DOTALL)
    print("[OK] Gráfico de ranking atualizado com comparativo!")
else:
    print("[AVISO] Padrão do gráfico de ranking não encontrado.")

open('relatorio_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_comparativo_receitas.html atualizado!")
