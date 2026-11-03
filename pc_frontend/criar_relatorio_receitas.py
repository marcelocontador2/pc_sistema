html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Comparativo de Receitas</title>
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
            font-size: 48px;
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
        .cover .footer {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 40px;
            font-style: italic;
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
            margin: 0 0 25px 0;
            font-weight: 800;
            letter-spacing: -0.5px;
        }
        .section-text {
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.7;
            margin-bottom: 25px;
        }

        /* CARDS */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .cards-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--bg-card);
            padding: 22px;
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
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .card .card-value {
            font-size: 26px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 5px;
        }
        .card .card-sub {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }
        .card .card-delta {
            font-size: 13px;
            font-weight: 600;
            margin-top: 5px;
        }
        .card .card-delta.positive { color: var(--success); }
        .card .card-delta.negative { color: var(--danger); }

        /* TABELAS */
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
        .badge.positive { background: #c6f6d5; color: #22543d; }
        .badge.negative { background: #fed7d7; color: #9b2c2c; }

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
        .chart-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .info-card {
            background: var(--bg-light);
            padding: 18px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
        }
        .info-card .info-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 5px;
        }
        .info-card .info-value {
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 3px;
        }
        .info-card .info-desc {
            font-size: 11px;
            color: var(--text-muted);
        }

        /* DESTAQUE ESCURO */
        .dark-box {
            background: var(--primary);
            color: #fff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: var(--shadow);
        }
        .dark-box .box-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--accent);
        }
        .dark-box .box-value {
            font-size: 48px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 10px;
        }
        .dark-box .box-desc {
            font-size: 13px;
            color: #cbd5e0;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .dark-box .list-item {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        /* BARRA DE PROGRESSO */
        .progress-bar {
            width: 100%;
            height: 30px;
            background: var(--bg-light);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            margin-bottom: 10px;
        }
        .progress-bar .progress-fill {
            height: 100%;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 12px;
            font-weight: 700;
        }
        .progress-bar .progress-rest {
            height: 100%;
            background: #e2e8f0;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 11px;
            color: var(--text-muted);
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
            .page:last-child { page-break-after: auto; }
            .cover { min-height: 260mm !important; display: flex !important; justify-content: center !important; padding: 0 !important; }
            .cover::before { height: 40px !important; }
            .cover h1 { font-size: 32px !important; margin-top: 60px !important; }
            .section-title { font-size: 18px !important; margin-bottom: 8px !important; }
            .cards-grid-4 { grid-template-columns: repeat(4, 1fr) !important; gap: 8px !important; }
            .card { padding: 10px !important; }
            .card .card-value { font-size: 16px !important; }
            table { font-size: 9px !important; }
            th, td { padding: 4px 6px !important; }
            canvas { display: none !important; }
            .canvas-img { display: block !important; max-width: 100% !important; height: auto !important; max-height: 240px !important; margin: 0 auto !important; }
            .btn-salvar { display: none !important; }
            .chart-container { flex-direction: column !important; gap: 8px !important; }
            .dark-box { padding: 12px !important; }
            .dark-box .box-value { font-size: 28px !important; }
        }
    </style>
</head>
<body>

    <!-- CAPA -->
    <div class="page cover">
        <div class="logo-area">COFEN</div>
        <h1>Relatório Comparativo<br>de Receitas</h1>
        <div class="subtitle" id="capa-periodo">Carregando...</div>
        <div class="divider"></div>
        <div class="footer">Sistema COFEN/CORENs — Análise de arrecadação, execução orçamentária e desempenho regional</div>
    </div>

    <!-- SUMÁRIO EXECUTIVO -->
    <div class="page">
        <div class="section-subtitle">VISÃO GERAL</div>
        <h2 class="section-title">Sumário Executivo</h2>
        <p class="section-text" id="sumario-texto">Carregando...</p>
        <div class="cards-grid-4">
            <div class="card">
                <div class="card-title">Receita Realizada (Atual)</div>
                <div class="card-value" id="kpi-realizado">R$ 0,00</div>
                <div class="card-sub" id="kpi-realizado-anterior">vs. R$ 0,00 em 2025</div>
            </div>
            <div class="card">
                <div class="card-title">Crescimento da Receita</div>
                <div class="card-value" id="kpi-crescimento">0,00%</div>
                <div class="card-sub">Realizado 2025 → 2026</div>
            </div>
            <div class="card">
                <div class="card-title">Receita Orçada (Atual)</div>
                <div class="card-value" id="kpi-orcado">R$ 0,00</div>
                <div class="card-sub" id="kpi-orcado-anterior">vs. R$ 0,00 em 2025</div>
            </div>
            <div class="card">
                <div class="card-title">Execução Orçamentária</div>
                <div class="card-value" id="kpi-execucao">0,00%</div>
                <div class="card-sub" id="kpi-execucao-delta">—</div>
            </div>
        </div>
    </div>

    <!-- INDICADORES GERAIS -->
    <div class="page">
        <div class="section-subtitle">INDICADORES</div>
        <h2 class="section-title">Indicadores Gerais de Receita</h2>
        <p class="section-text">Comparativo consolidado entre os períodos.</p>
        <div class="chart-container">
            <div style="flex: 2;">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Indicador</th>
                                <th class="text-right">2025</th>
                                <th class="text-right">2026</th>
                                <th class="text-right">Variação</th>
                            </tr>
                        </thead>
                        <tbody id="tabela-indicadores"></tbody>
                    </table>
                </div>
            </div>
            <div class="dark-box" style="flex: 1;">
                <div class="box-title">Execução Orçamentária 2026</div>
                <div class="box-value" id="dark-execucao">0,00%</div>
                <div class="box-desc">do orçamento anual aprovado já realizado até o período</div>
            </div>
        </div>
    </div>

    <!-- ANÁLISE POR GRUPO DE RECEITA -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Análise por Grupo de Receita</h2>
        <p class="section-text">Valores em R$ milhões.</p>
        <div class="chart-container">
            <div class="chart-box" style="flex: 1.5;">
                <canvas id="grafico-grupos"></canvas>
            </div>
            <div class="chart-info" style="flex: 1;">
                <div id="grupos-info"></div>
            </div>
        </div>
    </div>

    <!-- RANKING DOS CORENS -->
    <div class="page">
        <div class="section-subtitle">RANKING</div>
        <h2 class="section-title">Ranking dos CORENs por Arrecadação</h2>
        <p class="section-text">Top 10 regionais, valores em R$ milhões.</p>
        <div class="chart-box">
            <canvas id="grafico-ranking"></canvas>
        </div>
    </div>

    <!-- PARTICIPAÇÃO DOS PRINCIPAIS CORENS -->
    <div class="page">
        <div class="section-subtitle">PARTICIPAÇÃO</div>
        <h2 class="section-title">Participação dos Principais CORENs</h2>
        <p class="section-text">Participação na arrecadação total transferida ao COFEN.</p>
        <div class="chart-container">
            <div class="chart-box" style="flex: 1;">
                <canvas id="grafico-donut"></canvas>
            </div>
            <div class="dark-box" style="flex: 1;">
                <div class="box-title">Concentração da Arrecadação</div>
                <div class="box-value" id="dark-concentracao">0,00%</div>
                <div class="box-desc">da arrecadação total é concentrada nos 5 principais CORENs</div>
                <div id="lista-top5"></div>
            </div>
        </div>
    </div>

    <!-- PROJEÇÃO -->
    <div class="page">
        <div class="section-subtitle">PROJEÇÃO</div>
        <h2 class="section-title">Projeção para Encerramento do Ano</h2>
        <p class="section-text">Com base na execução acumulada até o período, observa-se trajetória compatível com o orçamento anual aprovado.</p>
        <div style="display: flex; gap: 30px; align-items: flex-start;">
            <div style="flex: 1;">
                <div style="font-size: 24px; font-weight: 800; color: var(--primary); margin-bottom: 15px;" id="projecao-pct">0,00%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="barra-realizado" style="width: 0%;">R$ 0,00 mi realizado</div>
                    <div class="progress-rest" id="barra-meta">Meta: R$ 0,00 mi</div>
                </div>
                <div style="display: flex; gap: 15px; margin-top: 20px;">
                    <div class="info-card" style="flex: 1;">
                        <div class="info-title">1º Semestre</div>
                        <div class="info-value" id="projecao-1sem">R$ 0,00 mi</div>
                        <div class="info-desc">Realizado (Jan–Jun)</div>
                    </div>
                    <div class="info-card" style="flex: 1;">
                        <div class="info-title">2º Semestre (projeção)</div>
                        <div class="info-value" id="projecao-2sem">R$ 0,00 mi</div>
                        <div class="info-desc">Necessário para atingir a meta</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- CONCLUSÃO -->
    <div class="page">
        <div class="section-subtitle">CONCLUSÃO</div>
        <h2 class="section-title">Conclusão</h2>
        <p class="section-text" id="conclusao-texto">Carregando...</p>
        <div id="conclusao-cards" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;"></div>
        <div style="text-align: right; margin-top: 30px;">
            <button class="btn-salvar" onclick="prepararImpressao()">📄 Imprimir / Salvar PDF</button>
        </div>
    </div>

    <script>
        function fmt(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
        function fmtPct(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }
        function fmtMi(v) { return 'R$ ' + (v/1000000).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' mi'; }

        const params = new URLSearchParams(window.location.search);
        const periodoAtual = params.get('periodo_atual') || '2026-TRIMESTRE-3';

        fetch(`/api/comparativo_receitas_v2/${periodoAtual}?_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                if (d.erro) { document.body.innerHTML = '<h1>Erro: ' + d.mensagem + '</h1>'; return; }
                
                const at = d.atual;
                const an = d.anterior;
                const varReceita = an.realizado_total > 0 ? ((at.realizado_total - an.realizado_total) / an.realizado_total) * 100 : 0;
                const varOrcado = an.orcado_total > 0 ? ((at.orcado_total - an.orcado_total) / an.orcado_total) * 100 : 0;

                // Capa
                document.getElementById('capa-periodo').innerText = `Período Atual vs. Período Anterior`;

                // Sumário
                document.getElementById('sumario-texto').innerText = `A arrecadação acumulada atingiu R$ ${fmt(at.realizado_total)} no período atual, contra R$ ${fmt(an.realizado_total)} no período anterior — crescimento de ${fmtPct(varReceita)}.`;

                // KPIs
                document.getElementById('kpi-realizado').innerText = fmtMi(at.realizado_total);
                document.getElementById('kpi-realizado-anterior').innerText = 'vs. ' + fmtMi(an.realizado_total);
                document.getElementById('kpi-crescimento').innerText = (varReceita >= 0 ? '+' : '') + fmtPct(varReceita);
                document.getElementById('kpi-orcado').innerText = fmtMi(at.orcado_total);
                document.getElementById('kpi-orcado-anterior').innerText = 'vs. ' + fmtMi(an.orcado_total);
                document.getElementById('kpi-execucao').innerText = fmtPct(at.percentual_total);
                const deltaExec = at.percentual_total - an.percentual_total;
                const deltaEl = document.getElementById('kpi-execucao-delta');
                deltaEl.innerText = (deltaExec >= 0 ? '+' : '') + fmtPct(deltaExec) + ' p.p.';
                deltaEl.className = 'card-delta ' + (deltaExec >= 0 ? 'positive' : 'negative');

                // Tabela Indicadores
                const tbodyInd = document.getElementById('tabela-indicadores');
                tbodyInd.innerHTML = `
                    <tr><td>Receita Orçada</td><td class="text-right">${fmt(an.orcado_total)}</td><td class="text-right">${fmt(at.orcado_total)}</td><td class="text-right"><span class="badge ${varOrcado >= 0 ? 'positive' : 'negative'}">${(varOrcado >= 0 ? '+' : '') + fmtPct(varOrcado)}</span></td></tr>
                    <tr><td>Receita Realizada</td><td class="text-right">${fmt(an.realizado_total)}</td><td class="text-right">${fmt(at.realizado_total)}</td><td class="text-right"><span class="badge ${varReceita >= 0 ? 'positive' : 'negative'}">${(varReceita >= 0 ? '+' : '') + fmtPct(varReceita)}</span></td></tr>
                    <tr class="total-row"><td>Percentual Executado</td><td class="text-right">${fmtPct(an.percentual_total)}</td><td class="text-right">${fmtPct(at.percentual_total)}</td><td class="text-right"><span class="badge ${deltaExec >= 0 ? 'positive' : 'negative'}">${(deltaExec >= 0 ? '+' : '') + fmtPct(deltaExec)} p.p.</span></td></tr>
                `;
                document.getElementById('dark-execucao').innerText = fmtPct(at.percentual_total);

                // Gráfico de Grupos
                const gruposAt = at.grupos.filter(g => g.realizado > 0 || g.orcado > 0);
                const gruposAn = an.grupos.filter(g => g.realizado > 0 || g.orcado > 0);
                const labelsGrupos = gruposAt.map(g => g.nome.length > 30 ? g.nome.substring(0, 30) + '...' : g.nome);
                
                new Chart(document.getElementById('grafico-grupos').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: labelsGrupos,
                        datasets: [
                            { label: '2025', data: gruposAn.map(g => g.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 },
                            { label: '2026', data: gruposAt.map(g => g.realizado / 1000000), backgroundColor: '#5b8fc9', borderRadius: 4 }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8, font: { family: 'Inter', size: 11 } } },
                            tooltip: { callbacks: { label: function(ctx) { return ctx.dataset.label + ': R$ ' + ctx.raw.toFixed(2) + ' mi'; } } }
                        },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#edf2f7' }, ticks: { font: { family: 'Inter', size: 10 } } },
                            x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 9 } } }
                        }
                    }
                });

                // Info dos Grupos
                const infoContainer = document.getElementById('grupos-info');
                infoContainer.innerHTML = '';
                gruposAt.slice(0, 3).forEach(g => {
                    const anGrupo = gruposAn.find(x => x.nome === g.nome);
                    const varGrupo = anGrupo && anGrupo.realizado > 0 ? ((g.realizado - anGrupo.realizado) / anGrupo.realizado) * 100 : 0;
                    infoContainer.innerHTML += `
                        <div class="info-card">
                            <div class="info-title">${g.nome}</div>
                            <div class="info-value" style="color: ${varGrupo >= 0 ? 'var(--success)' : 'var(--danger)'};">${(varGrupo >= 0 ? '+' : '') + fmtMi(g.realizado - (anGrupo ? anGrupo.realizado : 0))}</div>
                            <div class="info-desc">${varGrupo >= 0 ? 'Aumento' : 'Redução'} de ${fmtPct(Math.abs(varGrupo))} em relação ao período anterior</div>
                        </div>
                    `;
                });

                // Ranking dos CORENs
                const coresAt = at.cores.sort((a, b) => b.realizado - a.realizado).slice(0, 10);
                new Chart(document.getElementById('grafico-ranking').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: coresAt.map(c => c.nome),
                        datasets: [{ label: 'Arrecadação 2026 (R$ mi)', data: coresAt.map(c => c.realizado / 1000000), backgroundColor: '#0a1c3a', borderRadius: 4 }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx) { return 'R$ ' + ctx.raw.toFixed(2) + ' mi'; } } } },
                        scales: { x: { beginAtZero: true, grid: { color: '#edf2f7' }, ticks: { font: { family: 'Inter', size: 10 } } }, y: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 10 } } } }
                    }
                });

                // Donut de Participação
                const totalCores = coresAt.reduce((acc, c) => acc + c.realizado, 0);
                const top5 = coresAt.slice(0, 5);
                const outros = coresAt.slice(5).reduce((acc, c) => acc + c.realizado, 0);
                const labelsDonut = [...top5.map(c => c.nome), 'Demais CORENs'];
                const dataDonut = [...top5.map(c => c.realizado), outros];
                new Chart(document.getElementById('grafico-donut').getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: labelsDonut,
                        datasets: [{ data: dataDonut, backgroundColor: ['#0a1c3a', '#1a3b5c', '#2c5282', '#5b8fc9', '#a0c4e8', '#d0e2f2'], borderWidth: 2, borderColor: '#fff' }]
                    },
                    options: {
                        responsive: true,
                        cutout: '55%',
                        plugins: {
                            legend: { display: false },
                            datalabels: { color: '#fff', font: { weight: 'bold', size: 11 }, formatter: (v, ctx) => ((v/totalCores)*100).toFixed(1) + '%' }
                        }
                    },
                    plugins: [ChartDataLabels]
                });

                // Concentração Top 5
                const concTop5 = (top5.reduce((acc, c) => acc + c.realizado, 0) / totalCores) * 100;
                document.getElementById('dark-concentracao').innerText = fmtPct(concTop5);
                const listaTop5 = document.getElementById('lista-top5');
                listaTop5.innerHTML = '';
                top5.forEach(c => {
                    const pct = (c.realizado / totalCores) * 100;
                    listaTop5.innerHTML += `<div class="list-item"><span>${c.nome}</span><span>${fmtPct(pct)}</span></div>`;
                });

                // Projeção
                const pctExec = at.percentual_total;
                document.getElementById('projecao-pct').innerText = fmtPct(pctExec);
                const realizadoMi = at.realizado_total / 1000000;
                const metaMi = at.orcado_total / 1000000;
                document.getElementById('barra-realizado').style.width = pctExec + '%';
                document.getElementById('barra-realizado').innerText = 'R$ ' + realizadoMi.toFixed(2) + ' mi realizado';
                document.getElementById('barra-meta').innerText = 'Meta: R$ ' + metaMi.toFixed(2) + ' mi';
                const realizado1Sem = realizadoMi;
                const necessario2Sem = metaMi - realizadoMi;
                document.getElementById('projecao-1sem').innerText = 'R$ ' + realizado1Sem.toFixed(2) + ' mi';
                document.getElementById('projecao-2sem').innerText = 'R$ ' + necessario2Sem.toFixed(2) + ' mi';

                // Conclusão
                document.getElementById('conclusao-texto').innerText = `O Sistema COFEN/CORENs demonstra estabilidade arrecadatória, com manutenção dos níveis de execução orçamentária observados no período anterior.`;
                const concCards = document.getElementById('conclusao-cards');
                concCards.innerHTML = '';
                const conclusionItems = [];
                
                conclusionItems.push({ texto: `Crescimento da receita total (${(varReceita >= 0 ? '+' : '') + fmtPct(varReceita)})`, tipo: varReceita >= 0 ? 'positive' : 'negative' });
                conclusionItems.push({ texto: `Execução orçamentária em ${fmtPct(pctExec)}`, tipo: 'positive' });
                
                // Verifica grupos com maior variação
                const gruposVar = gruposAt.map(g => {
                    const anG = gruposAn.find(x => x.nome === g.nome);
                    const varG = anG && anG.realizado > 0 ? ((g.realizado - anG.realizado) / anG.realizado) * 100 : 0;
                    return { nome: g.nome, var: varG };
                }).sort((a, b) => Math.abs(b.var) - Math.abs(a.var));
                
                gruposVar.slice(0, 2).forEach(gv => {
                    conclusionItems.push({ texto: `${gv.nome}: ${(gv.var >= 0 ? '+' : '') + fmtPct(gv.var)}`, tipo: gv.var >= 0 ? 'positive' : 'negative' });
                });

                conclusionItems.forEach(item => {
                    concCards.innerHTML += `
                        <div style="background: var(--primary); color: #fff; padding: 18px; border-radius: 10px; display: flex; align-items: center; gap: 15px;">
                            <span style="font-size: 24px;">${item.tipo === 'positive' ? '▲' : '▼'}</span>
                            <span style="font-size: 13px; font-weight: 500;">${item.texto}</span>
                        </div>
                    `;
                });
            })
            .catch(e => console.error("Erro:", e));

        function prepararImpressao() {
            document.querySelectorAll('.canvas-img').forEach(img => img.remove());
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach(canvas => {
                try {
                    const img = document.createElement('img');
                    img.src = canvas.toDataURL('image/png');
                    img.className = 'canvas-img';
                    img.style.cssText = 'display: none; max-width: 100%; max-height: 240px; margin: 0 auto;';
                    canvas.parentNode.insertBefore(img, canvas.nextSibling);
                } catch (e) { console.error(e); }
            });
            document.querySelectorAll('.table-container').forEach(el => {
                el.style.maxHeight = 'none';
                el.style.overflow = 'visible';
            });
            setTimeout(() => {
                document.querySelectorAll('.canvas-img').forEach(img => img.style.display = 'block');
                window.print();
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
with open('relatorio_comparativo_receitas.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] relatorio_comparativo_receitas.html criado com o padrão visual!")
