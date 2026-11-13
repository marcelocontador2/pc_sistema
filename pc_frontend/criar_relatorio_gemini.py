html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório - Análise por Centro de Custos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0a1c3a;
            --secondary: #2c5282;
            --accent: #5b8fc9;
            --bg-light: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #1a202c;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --success: #38a169;
            --danger: #e53e3e;
            --shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
        }
        @page { margin: 0; size: A4; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-main);
            margin: 0;
            padding: 0;
            background: #fff;
            line-height: 1.5;
        }
        .page {
            padding: 50px 60px;
            page-break-after: always;
            position: relative;
            box-sizing: border-box;
            height: 100vh;
            overflow: hidden;
        }
        .page:last-child { page-break-after: auto; }

        /* CAPA */
        .cover {
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: linear-gradient(135deg, #fff 0%, #f0f4f9 100%);
            position: relative;
        }
        .cover::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 12px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
        }
        .cover .logo-area {
            font-size: 14px;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: 2px;
            margin-bottom: 30px;
        }
        .cover h1 {
            font-size: 52px;
            font-weight: 800;
            color: var(--primary);
            margin: 0;
            line-height: 1.1;
            letter-spacing: -1px;
        }
        .cover .subtitle {
            font-size: 18px;
            color: var(--text-muted);
            margin-top: 15px;
            font-weight: 500;
        }
        .cover .divider {
            width: 80px;
            height: 4px;
            background: var(--accent);
            margin: 30px 0;
            border-radius: 2px;
        }
        .cover .total-box {
            margin-top: 30px;
        }
        .cover .total-box .label {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        .cover .total-box .value {
            font-size: 36px;
            font-weight: 800;
            color: var(--primary);
            margin: 8px 0;
        }
        .cover .total-box .variation {
            font-size: 16px;
            font-weight: 600;
        }

        /* SEÇÕES */
        .section-subtitle {
            font-size: 12px;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 2.5px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .section-title {
            font-size: 32px;
            color: var(--primary);
            margin: 0 0 35px 0;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        /* CARDS */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 12px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent);
        }
        .card .card-title {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .card .card-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 5px;
        }
        .card .card-sub {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
        }

        /* TABELA */
        .table-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background: #fff;
        }
        th {
            background: var(--primary);
            color: #fff;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            font-weight: 500;
        }
        tr:nth-child(even) { background: var(--bg-light); }
        tr:last-child td { border-bottom: none; }
        .text-right { text-align: right; }
        .total-row td {
            font-weight: 800;
            background: var(--bg-light);
            color: var(--primary);
            border-top: 2px solid var(--primary);
        }
        .badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge.positive { background: #fed7d7; color: #9b2c2c; }
        .badge.negative { background: #c6f6d5; color: #22543d; }

        /* GRÁFICOS */
        .chart-container {
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        .chart-box {
            flex: 1;
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        .leitura-box {
            flex: 1;
            background: var(--primary);
            color: #fff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: var(--shadow);
        }
        .leitura-box h3 {
            color: var(--accent);
            margin-top: 0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        .leitura-box ul {
            padding-left: 20px;
            line-height: 1.8;
            font-size: 14px;
        }

        /* BOTÃO */
        .btn-salvar {
            padding: 14px 32px;
            background: var(--primary);
            color: #fff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
            box-shadow: var(--shadow);
            transition: all 0.2s;
        }
        .btn-salvar:hover { background: var(--secondary); transform: translateY(-1px); }

        /* NOTAS EXPLICATIVAS */
        .nota {
            background: #f8fafc;
            border-left: 4px solid var(--accent);
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.6;
            margin-top: 20px;
        }
        .nota strong { color: var(--primary); }

        @media print {
            @page {
                size: A4;
                margin: 15mm 15mm 15mm 15mm;
            }
            body {
                margin: 0;
                padding: 0;
                background: #fff;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .page {
                page-break-after: always;
                page-break-inside: avoid;
                height: auto !important;
                min-height: auto !important;
                overflow: visible !important;
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .cover {
                min-height: 260mm !important;
                display: flex !important;
                justify-content: center !important;
                padding: 0 !important;
            }
            .cover::before {
                height: 40px !important;
            }
            .cover h1 {
                font-size: 32px !important;
                margin-top: 60px !important;
            }
            .section-title {
                font-size: 18px !important;
                margin-bottom: 8px !important;
            }
            .cards-grid {
                gap: 8px !important;
            }
            .card {
                padding: 10px !important;
            }
            .card .card-value {
                font-size: 16px !important;
            }
            table {
                font-size: 9px !important;
            }
            th, td {
                padding: 4px 6px !important;
            }
            canvas {
                display: none !important;
            }
            .canvas-img {
                display: block !important;
                max-width: 100% !important;
                height: auto !important;
                max-height: 240px !important;
                margin: 0 auto !important;
            }
            .chart-container {
                flex-direction: column !important;
                gap: 8px !important;
            }
            .btn-salvar {
                display: none !important;
            }
            .leitura-box {
                padding: 8px !important;
                font-size: 9px !important;
            }
            .leitura-box h3 {
                font-size: 9px !important;
            }
            .leitura-box ul {
                font-size: 9px !important;
                padding-left: 15px !important;
            }
            .nota {
                font-size: 9px !important;
                padding: 8px 12px !important;
                margin-top: 10px !important;
            }
        }
    </style>
</head>
<body>

    <!-- CAPA -->
    <div class="page cover">
        <div class="logo-area">COFEN/BR</div>
        <h1>Análise de Despesas<br>Mensais por Centro de Custo</h1>
        <div class="subtitle">Comparativo de Períodos | Fase de Pagamento</div>
        <div class="divider"></div>
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
        <div class="nota">
            <strong>Nota 1:</strong> O total executado no período atual foi de <span id="nota-total">R$ 0,00</span>, com uma variação de <span id="nota-variacao">0,00%</span> em relação ao mesmo período do ano anterior. A média mensal é de <span id="nota-media">R$ 0,00</span>. O maior centro de custo é o <span id="nota-maior">-</span>, responsável por uma parcela significativa do total.
        </div>
    </div>

    <!-- TABELA DETALHADA -->
    <div class="page">
        <div class="section-subtitle">DADOS</div>
        <h2 class="section-title">Tabela Detalhada</h2>
        <div class="table-container">
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
        <div class="nota">
            <strong>Nota 2:</strong> A tabela acima detalha o gasto por centro de custo, comparando o período atual com o anterior. As variações positivas (em vermelho) indicam aumento no gasto, enquanto as negativas (em verde) indicam redução. O total geral do período atual é de <span id="nota-total-tabela">R$ 0,00</span>.
        </div>
    </div>

    <!-- GRÁFICO DE TENDÊNCIA -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div class="chart-container" style="margin-bottom: 30px;">
            <div class="chart-box" style="flex: 1.5; max-height: 300px;">
                <canvas id="grafico-tendencia" style="max-height: 280px;"></canvas>
            </div>
            <div class="leitura-box" style="flex: 1; max-height: 300px; overflow-y: auto;">
                <h3>LEITURA DO GRÁFICO</h3>
                <ul id="leitura-tendencia">
                    <li>Carregando...</li>
                </ul>
            </div>
        </div>
        
        <div class="table-container" style="margin-top: 15px; max-height: 320px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Mês</th>
                        <th class="text-right">Total Atual (R$)</th>
                        <th class="text-right">Total Anterior (R$)</th>
                        <th class="text-right">Variação (R$)</th>
                        <th class="text-right">Variação (%)</th>
                    </tr>
                </thead>
                <tbody id="tabela-mensal"></tbody>
            </table>
        </div>
        <div class="nota">
            <strong>Nota 3:</strong> O gráfico de tendência mostra a evolução mês a mês do gasto total, comparando o período atual (barras escuras) com o anterior (barras claras). Observa-se um pico significativo em SET no período anterior (R$ 42,5 mi), enquanto o período atual apresentou um pico em JUN (R$ 23,2 mi). A tabela acima detalha os valores mensais e as variações.
        </div>
    </div>

    <!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        <div class="chart-container">
            <div class="chart-box donut-container" style="flex: 1; max-width: 400px;">
                <canvas id="grafico-donut" style="max-height: 350px;"></canvas>
            </div>
            <div style="flex: 1.2; max-height: 400px; overflow-y: auto;">
                <div class="table-container">
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
        <div class="nota">
            <strong>Nota 4:</strong> O gráfico de composição (donut) mostra a distribuição percentual do gasto total entre os centros de custo no período atual. O centro 05 - Coordenação/Orientação concentra 34,58% do total, seguido pelo 06 - Despesas Administrativas (22,12%). Os 3 maiores centros somam 71,18% do gasto total, indicando alta concentração.
        </div>
    </div>

    <!-- CONCLUSÃO -->
    <div class="page">
        <div class="section-subtitle">CONCLUSÃO</div>
        <h2 class="section-title">Conclusão e Recomendações</h2>
        <div style="background: var(--bg-light); padding: 25px; border-radius: 12px; border-left: 4px solid var(--primary); margin-bottom: 20px;">
            <h3 style="color: var(--primary); margin-top: 0; font-size: 16px;">1. Conclusão sobre o Total Executado</h3>
            <p id="conclusao-total" contenteditable="true" style="font-size: 14px; line-height: 1.7; border: 1px dashed #ccc; padding: 12px; border-radius: 8px; background: #fff; margin: 0;">Carregando...</p>
        </div>
        <div style="background: var(--bg-light); padding: 25px; border-radius: 12px; border-left: 4px solid var(--secondary); margin-bottom: 20px;">
            <h3 style="color: var(--primary); margin-top: 0; font-size: 16px;">2. Análise de Concentração</h3>
            <p id="conclusao-concentracao" contenteditable="true" style="font-size: 14px; line-height: 1.7; border: 1px dashed #ccc; padding: 12px; border-radius: 8px; background: #fff; margin: 0;">Carregando...</p>
        </div>
        <div style="background: #fffaf0; padding: 25px; border-radius: 12px; border-left: 4px solid #dd6b20; margin-bottom: 20px;">
            <h3 style="color: #c05621; margin-top: 0; font-size: 16px;">3. Alertas e Pontos de Atenção</h3>
            <ul id="conclusao-alertas" contenteditable="true" style="font-size: 14px; line-height: 1.7; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 12px; border-radius: 8px; background: #fff;"></ul>
        </div>
        <div style="background: #f0fff4; padding: 25px; border-radius: 12px; border-left: 4px solid #38a169;">
            <h3 style="color: #22543d; margin-top: 0; font-size: 16px;">4. Recomendações</h3>
            <ul id="conclusao-recomendacoes" contenteditable="true" style="font-size: 14px; line-height: 1.7; padding-left: 20px; margin: 0; border: 1px dashed #ccc; padding: 12px; border-radius: 8px; background: #fff;"></ul>
        </div>
        <div class="nota" style="margin-top: 25px;">
            <strong>Nota 5:</strong> A conclusão acima foi gerada automaticamente com base nos dados do período. Os textos são editáveis (clique e digite) para ajustes antes da impressão. Use o botão abaixo para imprimir ou salvar como PDF.
        </div>
        <div style="text-align: right; margin-top: 25px;">
            <button class="btn-salvar" onclick="prepararImpressao()">📄 Imprimir / Salvar PDF</button>
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
                    varEl.style.color = 'var(--danger)';
                } else {
                    varEl.innerText = (d.variacao_pct >= 0 ? '▲ ' : '▼ ') + fmtPct(Math.abs(d.variacao_pct)) + ' vs. Período Anterior';
                    varEl.style.color = d.variacao_pct >= 0 ? 'var(--danger)' : 'var(--success)';
                }

                // KPIs
                document.getElementById('kpi-total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                document.getElementById('kpi-total-anterior').innerText = d.anterior.total > 0 ? 'Anterior: R$ ' + fmt(d.anterior.total) : 'N/A';
                document.getElementById('kpi-media-atual').innerText = 'R$ ' + fmt(d.atual.media_mensal);
                document.getElementById('kpi-media-anterior').innerText = d.anterior.media_mensal > 0 ? 'Anterior: R$ ' + fmt(d.anterior.media_mensal) : 'N/A';
                document.getElementById('kpi-maior-centro').innerText = d.atual.maior_centro.nome;
                document.getElementById('kpi-maior-valor').innerText = 'R$ ' + fmt(d.atual.maior_centro.valor);
                document.getElementById('kpi-variacao').innerText = fmtPct(d.variacao_pct);

                // Nota 1
                document.getElementById('nota-total').innerText = 'R$ ' + fmt(d.atual.total);
                document.getElementById('nota-variacao').innerText = fmtPct(d.variacao_pct);
                document.getElementById('nota-media').innerText = 'R$ ' + fmt(d.atual.media_mensal);
                document.getElementById('nota-maior').innerText = d.atual.maior_centro.nome;

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
                document.getElementById('nota-total-tabela').innerText = 'R$ ' + fmt(d.atual.total);

                // Gráfico de Tendência
                const meses = d.atual.meses_disponiveis || ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET"];
                const valoresAtual = meses.map(m => d.atual.meses[m] || 0);
                const valoresAnterior = meses.map(m => (d.anterior.meses || {})[m] || 0);
                
                new Chart(document.getElementById('grafico-tendencia').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: meses,
                        datasets: [
                            { label: 'Período Atual', data: valoresAtual, backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: 'Período Anterior', data: valoresAnterior, backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8, font: { family: 'Inter', size: 12 } } },
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
                                grid: { color: '#edf2f7' },
                                ticks: {
                                    font: { family: 'Inter', size: 11 },
                                    callback: function(value) { return 'R$ ' + (value/1000000).toFixed(1) + 'M'; }
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Inter', size: 11 } }
                            }
                        }
                    }
                });

                // Leitura do Gráfico
                let maiorMes = meses[0], menorMes = meses[0];
                meses.forEach(m => {
                    if ((d.atual.meses[m] || 0) > (d.atual.meses[maiorMes] || 0)) maiorMes = m;
                    if ((d.atual.meses[m] || 0) < (d.atual.meses[menorMes] || 0)) menorMes = m;
                });
                document.getElementById('leitura-tendencia').innerHTML = `
                    <li>O maior gasto ocorreu em <strong>${maiorMes}</strong>, com R$ ${fmt(d.atual.meses[maiorMes] || 0)}.</li>
                    <li>O menor gasto foi em <strong>${menorMes}</strong>, com R$ ${fmt(d.atual.meses[menorMes] || 0)}.</li>
                    <li>A média mensal do período é de R$ ${fmt(d.atual.media_mensal)}.</li>
                `;

                // Tabela Mensal
                const tbodyMensal = document.getElementById('tabela-mensal');
                if (tbodyMensal) {
                    tbodyMensal.innerHTML = '';
                    meses.forEach(m => {
                        const at = d.atual.meses[m] || 0;
                        const an = (d.anterior.meses || {})[m] || 0;
                        const varM = at - an;
                        const varPctM = an > 0 ? (varM / an) * 100 : (at > 0 ? 100 : 0);
                        const badgeClassM = varM >= 0 ? 'positive' : 'negative';
                        tbodyMensal.innerHTML += `
                            <tr>
                                <td>${m}</td>
                                <td class="text-right">${fmt(at)}</td>
                                <td class="text-right">${fmt(an)}</td>
                                <td class="text-right">${fmt(varM)}</td>
                                <td class="text-right"><span class="badge ${badgeClassM}">${fmtPct(varPctM)}</span></td>
                            </tr>
                        `;
                    });
                    
                    const totalAtualMes = valoresAtual.reduce((a, b) => a + b, 0);
                    const totalAnteriorMes = valoresAnterior.reduce((a, b) => a + b, 0);
                    const varTotalMes = totalAtualMes - totalAnteriorMes;
                    const varTotalMesPct = totalAnteriorMes > 0 ? (varTotalMes / totalAnteriorMes) * 100 : 0;
                    tbodyMensal.innerHTML += `
                        <tr class="total-row">
                            <td>TOTAL</td>
                            <td class="text-right">${fmt(totalAtualMes)}</td>
                            <td class="text-right">${fmt(totalAnteriorMes)}</td>
                            <td class="text-right">${fmt(varTotalMes)}</td>
                            <td class="text-right"><span class="badge ${varTotalMes >= 0 ? 'positive' : 'negative'}">${fmtPct(varTotalMesPct)}</span></td>
                        </tr>
                    `;
                }

                // Gráfico de Donut
                const centros = d.atual.centros.sort((a, b) => b.valor - a.valor);
                const labels = centros.map(c => { const m = c.nome.match(/AF\\s*\\d+/i); return m ? m[0].toUpperCase() : c.nome.substring(0, 10); });
                const dataValores = centros.map(c => c.valor);
                const total = d.atual.total;
                new Chart(document.getElementById('grafico-donut').getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{ data: dataValores, backgroundColor: ['#0a1c3a', '#1a3b5c', '#2c5282', '#5b8fc9', '#a0c4e8', '#d0e2f2'], borderWidth: 2, borderColor: '#fff' }]
                    },
                    options: {
                        responsive: true,
                        cutout: '55%',
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                color: '#fff',
                                font: { weight: 'bold', size: 12 },
                                formatter: (v, ctx) => ((v/total)*100).toFixed(1) + '%'
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });

                // Tabela de Composição
                const tbodyComp = document.querySelector('#tabela-composicao tbody');
                tbodyComp.innerHTML = '';
                centros.forEach(c => {
                    const pct = total > 0 ? (c.valor / total) * 100 : 0;
                    tbodyComp.innerHTML += `
                        <tr>
                            <td>${c.nome}</td>
                            <td class="text-right">${fmt(c.valor)}</td>
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

        function prepararImpressao() {
            // Remove imagens antigas
            document.querySelectorAll('.canvas-img').forEach(img => img.remove());
            
            // Converte cada canvas em imagem
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach(canvas => {
                try {
                    const img = document.createElement('img');
                    img.src = canvas.toDataURL('image/png');
                    img.className = 'canvas-img';
                    img.style.cssText = 'display: none; max-width: 100%; max-height: 240px; margin: 0 auto;';
                    canvas.parentNode.insertBefore(img, canvas.nextSibling);
                } catch (e) {
                    console.error('Erro ao converter canvas:', e);
                }
            });
            
            // Remove restrições de altura das tabelas para não cortar
            document.querySelectorAll('.table-container').forEach(el => {
                el.style.maxHeight = 'none';
                el.style.overflow = 'visible';
            });
            
            // Ativa a impressão
            setTimeout(() => {
                document.querySelectorAll('.canvas-img').forEach(img => {
                    img.style.display = 'block';
                });
                window.print();
                
                // Restaura após impressão
                setTimeout(() => {
                    document.querySelectorAll('.canvas-img').forEach(img => img.remove());
                    document.querySelectorAll('canvas').forEach(c => c.style.display = 'block');
                }, 1000);
            }, 200);
        }
    </script>
</body>
</html>
"""

with open('relatorio_final.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] relatorio_final.html recriado com o padrão Gemini (notas explicativas e design moderno)!")
