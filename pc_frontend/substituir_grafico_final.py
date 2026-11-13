import re

c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Padrão para encontrar o bloco do gráfico de tendência
padrao = r'// 1\. Gráfico de Tendência \(Barras\).*?new Chart\(ctxTendencia, \{.*?\}\);'

novo_bloco = '''// 1. Gráfico de Tendência (Barras - Comparativo Anual)
                const meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"];
                const valoresAtual = meses.map(m => d.atual.meses[m] || 0);
                const valoresAnterior = meses.map(m => (d.anterior && d.anterior.meses) ? (d.anterior.meses[m] || 0) : 0);
                
                const ctxTendencia = document.getElementById('grafico-tendencia').getContext('2d');
                new Chart(ctxTendencia, {
                    type: 'bar',
                    data: {
                        labels: meses,
                        datasets: [
                            {
                                label: 'Período Atual (R$)',
                                data: valoresAtual,
                                backgroundColor: '#0a1c3a',
                                borderRadius: 4
                            },
                            {
                                label: 'Período Anterior (R$)',
                                data: valoresAnterior,
                                backgroundColor: '#5b8fc9',
                                borderRadius: 4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: true, position: 'top' }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return 'R$ ' + (value / 1000000).toFixed(1) + 'M';
                                    }
                                }
                            }
                        }
                    }
                });'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Gráfico de tendência substituído com comparativo anual!")
else:
    print("[AVISO] Padrão não encontrado. Tentando substituir manualmente...")
    # Fallback: substitui o bloco inteiro do gráfico
    inicio = c.find('// 1. Gráfico de Tendência')
    if inicio != -1:
        fim = c.find('});', inicio) + 3
        if fim > inicio:
            c = c[:inicio] + novo_bloco + c[fim:]
            print("[OK] Gráfico substituído manualmente!")

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado!")
