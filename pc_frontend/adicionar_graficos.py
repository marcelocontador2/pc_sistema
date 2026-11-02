c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Adiciona o Chart.js no head
if "chart.js" not in c:
    c = c.replace(
        "</head>",
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>'
    )

# Adiciona as novas seções antes do fechamento do body
novas_secoes = """
    <!-- TENDÊNCIA MENSAL -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div style="display: flex; gap: 20px; align-items: flex-start;">
            <div style="flex: 2; max-width: 600px;">
                <canvas id="grafico-tendencia"></canvas>
            </div>
            <div class="leitura-grafico" style="flex: 1; background: var(--primary); color: #fff; padding: 20px; border-radius: 8px; font-size: 13px;">
                <h3 style="color: var(--secondary); margin-top: 0;">LEITURA DO GRÁFICO</h3>
                <ul style="padding-left: 20px; line-height: 1.6;">
                    <li>O gasto mensal apresenta variações ao longo do semestre.</li>
                    <li>Março e Maio registraram os maiores picos de execução.</li>
                    <li>Os meses de Janeiro e Fevereiro tiveram os menores gastos.</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- DISTRIBUIÇÃO POR CENTRO DE CUSTO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        <div style="display: flex; gap: 20px; align-items: flex-start;">
            <div style="flex: 1; max-width: 400px;">
                <canvas id="grafico-donut"></canvas>
            </div>
            <div style="flex: 1;">
                <table id="tabela-composicao">
                    <thead>
                        <tr>
                            <th>Centro de Custo</th>
                            <th class="text-right">Total (R$)</th>
                            <th class="text-right">%</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- SCRIPT DOS GRÁFICOS -->
    <script>
        // Esse script vai rodar depois que os dados forem carregados
        window.addEventListener('load', function() {
            setTimeout(function() {
                // Pega os dados do objeto global (preenchido pelo fetch principal)
                if (!window.dadosRelatorio) {
                    console.error("Dados do relatório não encontrados.");
                    return;
                }
                const d = window.dadosRelatorio;
                
                // 1. Gráfico de Tendência (Barras)
                const meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"];
                const valores = meses.map(m => d.atual.meses[m] || 0);
                
                const ctxTendencia = document.getElementById('grafico-tendencia').getContext('2d');
                new Chart(ctxTendencia, {
                    type: 'bar',
                    data: {
                        labels: meses,
                        datasets: [{
                            label: 'Total Executado (R$)',
                            data: valores,
                            backgroundColor: '#2c5282',
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
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
                });
                
                // 2. Gráfico de Donut
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
                });
                
                // 3. Tabela de Composição
                const tbody = document.querySelector('#tabela-composicao tbody');
                tbody.innerHTML = '';
                const total = d.atual.total;
                centros.forEach(c => {
                    const pct = total > 0 ? (c.valor / total) * 100 : 0;
                    tbody.innerHTML += `
                        <tr>
                            <td>${c.nome}</td>
                            <td class="text-right">R$ ${fmt(c.valor)}</td>
                            <td class="text-right">${fmtPct(pct)}</td>
                        </tr>
                    `;
                });
            }, 2000); // Espera 2 segundos para o fetch principal popular window.dadosRelatorio
        });
    </script>
</body>
"""

c = c.replace("</body>", novas_secoes)

# Armazena os dados do fetch principal no objeto global
c = c.replace(
    ".then(d => {",
    ".then(d => { window.dadosRelatorio = d;"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Gráficos adicionados ao relatório!")
