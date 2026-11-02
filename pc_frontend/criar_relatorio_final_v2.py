html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório - Análise por Centro de Custos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        :root {
            --primary: #0a1c3a;
            --secondary: #5b8fc9;
            --bg-light: #eef4f9;
            --text-main: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
        }
        @page { margin: 0; size: A4; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text-main);
            margin: 0;
            padding: 0;
            background: #fff;
        }
        .page {
            padding: 40px;
            page-break-after: always;
            position: relative;
            box-sizing: border-box;
            height: 100vh;
        }
        .page:last-child { page-break-after: auto; }
        
        /* Capa */
        .cover {
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #fff;
            position: relative;
        }
        .cover::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 80px;
            background: var(--primary);
        }
        .cover h1 {
            font-size: 48px;
            color: var(--primary);
            margin: 120px 0 0 0;
            line-height: 1.1;
        }
        .cover .subtitle {
            font-size: 18px;
            color: var(--text-muted);
            margin-top: 20px;
        }
        .cover .total-box { margin-top: 40px; }
        .cover .total-box .label {
            font-size: 14px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .cover .total-box .value {
            font-size: 32px;
            font-weight: bold;
            color: var(--primary);
        }
        .cover .total-box .variation {
            font-size: 16px;
            font-weight: bold;
        }

        /* Seções */
        .section-title {
            font-size: 28px;
            color: var(--primary);
            margin-bottom: 30px;
        }
        .section-subtitle {
            font-size: 12px;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }

        /* Cards */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        .card {
            background: var(--bg-light);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--secondary);
        }
        .card .card-title {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .card .card-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--primary);
        }
        .card .card-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 10px;
        }

        /* Tabela */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 13px;
        }
        th {
            background: var(--primary);
            color: #fff;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }
        tr:nth-child(even) { background: var(--bg-light); }
        .text-right { text-align: right; }
        .total-row { font-weight: bold; background: var(--bg-light); }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge.positive { background: #f8d7da; color: #721c24; }
        .badge.negative { background: #d4edda; color: #155724; }

        /* Gráficos */
        .chart-container {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            margin-top: 20px;
        }
        .chart-box {
            flex: 1;
            max-width: 600px;
        }
        .leitura-box {
            flex: 1;
            background: var(--primary);
            color: #fff;
            padding: 20px;
            border-radius: 8px;
            font-size: 13px;
        }
        .leitura-box h3 {
            color: var(--secondary);
            margin-top: 0;
        }
        .leitura-box ul {
            padding-left: 20px;
            line-height: 1.6;
        }

        /* Botão */
        .btn-salvar {
            padding: 12px 24px;
            background: var(--primary);
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        @media print {
            .btn-salvar { display: none !important; }
            .page { height: auto; min-height: 100vh; }
        }
    </style>
</head>
<body>

    <!-- CAPA -->
    <div class="page cover">
        <div class="section-subtitle">COFEN/BR</div>
        <h1>Análise de Despesas Mensais<br>por Centro de Custo</h1>
        <div class="subtitle">Comparativo de Períodos | Fase de Pagamento</div>
        <div class="total-box">
            <div class="label">Total Executado (Atual)</div>
            <div class="value" id="total-atual">R$ 0,00</div>
            <div class="variation" id="variacao-total"></div>
        </div>
    </div>

    <!-- SUMÁRIO EXECUTIVO -->
    <div class="page">
        <div class="section-subtitle">VISÃO GERAL</div>
        <h2 class="section-title">Sumário Executivo</h2>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Total Executado (Atual)</div>
                <div class="card-value" id="kpi-total-atual">R$ 0,00</div>
                <div class="card-sub" id="kpi-total-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card">
                <div class="card-title">Média Mensal (Atual)</div>
                <div class="card-value" id="kpi-media-atual">R$ 0,00</div>
                <div class="card-sub" id="kpi-media-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card">
                <div class="card-title">Maior Centro de Custo</div>
                <div class="card-value" id="kpi-maior-centro">-</div>
                <div class="card-sub" id="kpi-maior-valor">R$ 0,00</div>
            </div>
            <div class="card">
                <div class="card-title">Variação Global</div>
                <div class="card-value" id="kpi-variacao">0,00%</div>
                <div class="card-sub">Atual vs. Anterior</div>
            </div>
        </div>
    </div>

    <!-- TABELA DETALHADA -->
    <div class="page">
        <div class="section-subtitle">DADOS</div>
        <h2 class="section-title">Tabela Detalhada — Despesas por Centro de Custo</h2>
        <table>
            <thead>
                <tr>
                    <th>Centro de Custo</th>
                    <th class="text-right">Total Atual (R$)</th>
                    <th class="text-right">Total Anterior (R$)</th>
                    <th class="text-right">Variação (R$)</th>
                    <th class="text-right">Variação (%)</th>
                </tr>
            </thead>
            <tbody id="tabela-corpo"></tbody>
        </table>
    </div>

    <!-- GRÁFICO DE TENDÊNCIA -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div class="chart-container">
            <div class="chart-box">
                <canvas id="grafico-tendencia"></canvas>
            </div>
            <div class="leitura-box">
                <h3>LEITURA DO GRÁFICO</h3>
                <ul id="leitura-tendencia">
                    <li>Carregando...</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        <div class="chart-container">
            <div class="chart-box">
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

    <!-- CONCLUSÃO -->
    <div class="page">
        <div class="section-subtitle">CONCLUSÃO</div>
        <h2 class="section-title">Conclusão e Recomendações</h2>
        <div style="background: var(--bg-light); padding: 20px; border-radius: 8px; border-left: 4px solid var(--primary); margin-bottom: 20px;">
            <h3 style="color: var(--primary); margin-top: 0;">1. Conclusão sobre o Total Executado</h3>
            <p id="conclusao-total" contenteditable="true" style="font-size: 14px; line-height: 1.6; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">Carregando...</p>
        </div>
        <div style="background: var(--bg-light); padding: 20px; border-radius: 8px; border-left: 4px solid var(--secondary); margin-bottom: 20px;">
            <h3 style="color: var(--primary); margin-top: 0;">2. Análise de Concentração</h3>
            <p id="conclusao-concentracao" contenteditable="true" style="font-size: 14px; line-height: 1.6; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;">Carregando...</p>
        </div>
        <div style="background: #fff8e1; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
            <h3 style="color: #856404; margin-top: 0;">3. Alertas e Pontos de Atenção</h3>
            <ul id="conclusao-alertas" contenteditable="true" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;"></ul>
        </div>
        <div style="background: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
            <h3 style="color: #155724; margin-top: 0;">4. Recomendações</h3>
            <ul id="conclusao-recomendacoes" contenteditable="true" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 10px; border-radius: 4px; background: #fff;"></ul>
        </div>
        <div style="text-align: right; margin-top: 20px;">
            <button class="btn-salvar" onclick="window.print()">📄 Imprimir / Salvar PDF</button>
        </div>
    </div>

    <script>
        function fmt(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
        function fmtPct(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }

        const params = new URLSearchParams(window.location.search);
        const periodoAtual = params.get('periodo_atual') || '2026-TRIMESTRE-3';

        fetch(`/api/relatorio_v2/${periodoAtual}?_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                // Capa
                document.getElementById('total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                const varEl = document.getElementById('variacao-total');
                if (d.anterior.total === 0) {
                    varEl.innerText = 'Sem dados para comparação';
                    varEl.style.color = '#dc3545';
                } else {
                    varEl.innerText = (d.variacao_pct >= 0 ? '▲ ' : '▼ ') + fmtPct(Math.abs(d.variacao_pct)) + ' vs. Período Anterior';
                    varEl.style.color = d.variacao_pct >= 0 ? '#dc3545' : '#28a745';
                }

                // KPIs
                document.getElementById('kpi-total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                document.getElementById('kpi-total-anterior').innerText = d.anterior.total > 0 ? 'Anterior: R$ ' + fmt(d.anterior.total) : 'N/A';
                document.getElementById('kpi-media-atual').innerText = 'R$ ' + fmt(d.atual.media_mensal);
                document.getElementById('kpi-media-anterior').innerText = d.anterior.media_mensal > 0 ? 'Anterior: R$ ' + fmt(d.anterior.media_mensal) : 'N/A';
                document.getElementById('kpi-maior-centro').innerText = d.atual.maior_centro.nome;
                document.getElementById('kpi-maior-valor').innerText = 'R$ ' + fmt(d.atual.maior_centro.valor);
                document.getElementById('kpi-variacao').innerText = fmtPct(d.variacao_pct);

                // Tabela Detalhada
                const tbody = document.getElementById('tabela-corpo');
                tbody.innerHTML = '';
                const mapa = {};
                d.atual.centros.forEach(c => { mapa[c.nome] = { atual: c.valor, anterior: 0 }; });
                (d.anterior.centros || []).forEach(c => {
                    if (mapa[c.nome]) mapa[c.nome].anterior = c.valor;
                    else mapa[c.nome] = { atual: 0, anterior: c.valor };
                });
                const ordenados = Object.keys(mapa).filter(nome => !nome.includes('Centro de Custo')).sort((a, b) => mapa[b].atual - mapa[a].atual);
                ordenados.forEach(nome => {
                    const at = mapa[nome].atual;
                    const an = mapa[nome].anterior;
                    const variacao = at - an;
                    const variacaoPct = an > 0 ? (variacao / an) * 100 : (at > 0 ? 100 : 0);
                    const badgeClass = variacao >= 0 ? 'positive' : 'negative';
                    tbody.innerHTML += `
                        <tr>
                            <td>${nome}</td>
                            <td class="text-right">${fmt(at)}</td>
                            <td class="text-right">${fmt(an)}</td>
                            <td class="text-right">${fmt(variacao)}</td>
                            <td class="text-right"><span class="badge ${badgeClass}">${fmtPct(variacaoPct)}</span></td>
                        </tr>
                    `;
                });
                tbody.innerHTML += `
                    <tr class="total-row">
                        <td>TOTAL GERAL</td>
                        <td class="text-right">${fmt(d.atual.total)}</td>
                        <td class="text-right">${fmt(d.anterior.total)}</td>
                        <td class="text-right">${fmt(d.variacao_total)}</td>
                        <td class="text-right"><span class="badge ${d.variacao_pct >= 0 ? 'positive' : 'negative'}">${fmtPct(d.variacao_pct)}</span></td>
                    </tr>
                `;

                // Gráfico de Tendência (Comparativo)
                const meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"];
                const valoresAtual = meses.map(m => d.atual.meses[m] || 0);
                const valoresAnterior = meses.map(m => (d.anterior.meses || {})[m] || 0);
                new Chart(document.getElementById('grafico-tendencia').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: meses,
                        datasets: [
                            { label: 'Período Atual', data: valoresAtual, backgroundColor: '#0a1c3a' },
                            { label: 'Período Anterior', data: valoresAnterior, backgroundColor: '#5b8fc9' }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.dataset.label + ': R$ ' + fmt(context.raw);
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) { return 'R$ ' + (value/1000000).toFixed(1) + 'M'; }
                                }
                            }
                        }
                    }
                });

                // Leitura do Gráfico (dinâmica)
                const maiorMes = meses.reduce((a, b) => (d.atual.meses[a] || 0) > (d.atual.meses[b] || 0) ? a : b);
                const menorMes = meses.reduce((a, b) => (d.atual.meses[a] || 0) < (d.atual.meses[b] || 0) ? a : b);
                document.getElementById('leitura-tendencia').innerHTML = `
                    <li>O maior gasto ocorreu em <strong>${maiorMes}</strong>, com R$ ${fmt(d.atual.meses[maiorMes] || 0)}.</li>
                    <li>O menor gasto foi em <strong>${menorMes}</strong>, com R$ ${fmt(d.atual.meses[menorMes] || 0)}.</li>
                    <li>A média mensal do período é de R$ ${fmt(d.atual.media_mensal)}.</li>
                `;

                // Gráfico de Donut
                const centros = d.atual.centros.sort((a, b) => b.valor - a.valor);
                const labels = centros.map(c => { const m = c.nome.match(/AF\\s*\\d+/i); return m ? m[0].toUpperCase() : c.nome.substring(0, 10); });
                const dataValores = centros.map(c => c.valor);
                const total = d.atual.total;
                new Chart(document.getElementById('grafico-donut').getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{ data: dataValores, backgroundColor: ['#0a1c3a', '#1a3b5c', '#2c5282', '#5b8fc9', '#a0c4e8', '#d0e2f2'] }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                color: '#fff',
                                font: { weight: 'bold' },
                                formatter: (v, ctx) => ((v/total)*100).toFixed(1) + '%'
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });

                // Tabela de Composição (ao lado do donut)
                const tbodyComp = document.querySelector('#tabela-composicao tbody');
                tbodyComp.innerHTML = '';
                centros.forEach(c => {
                    const pct = total > 0 ? (c.valor / total) * 100 : 0;
                    tbodyComp.innerHTML += `
                        <tr>
                            <td>${c.nome}</td>
                            <td class="text-right">R$ ${fmt(c.valor)}</td>
                            <td class="text-right">${fmtPct(pct)}</td>
                        </tr>
                    `;
                });

                // Conclusão
                document.getElementById('conclusao-total').innerHTML = `O total executado foi de <strong>R$ ${fmt(d.atual.total)}</strong>, com variação de <strong>${fmtPct(d.variacao_pct)}</strong> em relação ao período anterior.`;
                
                const top3 = centros.slice(0, 3);
                const somaTop3 = top3.reduce((acc, c) => acc + c.valor, 0);
                document.getElementById('conclusao-concentracao').innerHTML = `Os 3 maiores centros concentram <strong>${fmtPct((somaTop3/total)*100)}</strong> do total.`;

                const alertas = [];
                if (d.variacao_pct > 10) alertas.push(`Aumento de ${fmtPct(d.variacao_pct)} em relação ao período anterior.`);
                else if (d.variacao_pct < -10) alertas.push(`Redução de ${fmtPct(Math.abs(d.variacao_pct))} em relação ao período anterior.`);
                else alertas.push(`Variação estável (${fmtPct(d.variacao_pct)}).`);
                document.getElementById('conclusao-alertas').innerHTML = alertas.map(a => `<li>${a}</li>`).join('');

                document.getElementById('conclusao-recomendacoes').innerHTML = `<li>Monitorar os 3 maiores centros de custo.</li><li>Investigar variações atípicas.</li>`;
            })
            .catch(e => console.error("Erro:", e));
    </script>
</body>
</html>
"""

with open('relatorio_final.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] relatorio_final.html recriado com o padrão dos modelos!")
