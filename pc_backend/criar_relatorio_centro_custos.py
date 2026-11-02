html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório - Análise por Centro de Custos</title>
    <style>
        :root {
            --primary: #0a1c3a;
            --secondary: #5b8fc9;
            --bg-light: #eef4f9;
            --text-main: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --success: #28a745;
            --danger: #dc3545;
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
            background: linear-gradient(135deg, #fff 60%, var(--primary) 60%);
        }
        .cover h1 { font-size: 48px; color: var(--primary); margin: 0; line-height: 1.1; }
        .cover .subtitle { font-size: 18px; color: var(--text-muted); margin-top: 20px; }
        .cover .total-box { margin-top: 40px; }
        .cover .total-box .label { font-size: 14px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .cover .total-box .value { font-size: 32px; font-weight: bold; color: var(--primary); }
        .cover .total-box .variation { font-size: 16px; font-weight: bold; }
        .cover .variation.positive { color: var(--danger); }
        .cover .variation.negative { color: var(--success); }

        /* Títulos de Seção */
        .section-title { font-size: 28px; color: var(--primary); margin-bottom: 30px; }
        .section-subtitle { font-size: 12px; color: var(--secondary); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }

        /* Cards */
        .cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }
        .card {
            background: var(--bg-light);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--secondary);
        }
        .card .card-title { font-size: 12px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; }
        .card .card-value { font-size: 24px; font-weight: bold; color: var(--primary); }
        .card .card-sub { font-size: 12px; color: var(--text-muted); margin-top: 10px; }

        /* Tabela */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        th { background: var(--primary); color: #fff; padding: 12px; text-align: left; font-weight: 600; }
        td { padding: 12px; border-bottom: 1px solid var(--border-color); }
        tr:nth-child(even) { background: var(--bg-light); }
        .text-right { text-align: right; }
        .total-row { font-weight: bold; background: var(--bg-light); }

        /* Badges */
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge.positive { background: #f8d7da; color: #721c24; }
        .badge.negative { background: #d4edda; color: #155724; }
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
            <tbody id="tabela-corpo">
                <!-- Preenchido via JS -->
            </tbody>
        </table>
    </div>

    <script>
        function fmt(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
        function fmtPct(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }

        // Parâmetros da URL (pode ser ajustado para pegar da tela)
        const params = new URLSearchParams(window.location.search);
        const periodoAtual = params.get('periodo_atual') || '2026-TRIMESTRE-3';
        const periodoAnterior = params.get('periodo_anterior') || '2026-TRIMESTRE-2';

        fetch(`/api/relatorio_centro_custos?periodo_atual=${periodoAtual}&periodo_anterior=${periodoAnterior}&_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                // Capa
                document.getElementById('total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                const varEl = document.getElementById('variacao-total');
                varEl.innerText = (d.variacao_pct >= 0 ? '▲' : '▼') + ' ' + fmtPct(Math.abs(d.variacao_pct)) + ' vs. Período Anterior';
                varEl.className = 'variation ' + (d.variacao_pct >= 0 ? 'positive' : 'negative');

                // KPIs
                document.getElementById('kpi-total-atual').innerText = 'R$ ' + fmt(d.atual.total);
                document.getElementById('kpi-total-anterior').innerText = 'Anterior: R$ ' + fmt(d.anterior.total);
                document.getElementById('kpi-media-atual').innerText = 'R$ ' + fmt(d.atual.media_mensal);
                document.getElementById('kpi-media-anterior').innerText = 'Anterior: R$ ' + fmt(d.anterior.media_mensal);
                document.getElementById('kpi-maior-centro').innerText = d.atual.maior_centro.nome;
                document.getElementById('kpi-maior-valor').innerText = 'R$ ' + fmt(d.atual.maior_centro.valor);
                document.getElementById('kpi-variacao').innerText = fmtPct(d.variacao_pct);

                // Tabela
                const tbody = document.getElementById('tabela-corpo');
                tbody.innerHTML = '';
                // Combina os centros atuais e anteriores
                const mapa = {};
                d.atual.centros.forEach(c => { mapa[c.nome] = { atual: c.valor, anterior: 0 }; });
                d.anterior.centros.forEach(c => { 
                    if (mapa[c.nome]) mapa[c.nome].anterior = c.valor;
                    else mapa[c.nome] = { atual: 0, anterior: c.valor };
                });
                // Ordena pelo valor atual
                const ordenados = Object.keys(mapa).sort((a, b) => mapa[b].atual - mapa[a].atual);
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
                // Linha de total
                tbody.innerHTML += `
                    <tr class="total-row">
                        <td>TOTAL GERAL</td>
                        <td class="text-right">${fmt(d.atual.total)}</td>
                        <td class="text-right">${fmt(d.anterior.total)}</td>
                        <td class="text-right">${fmt(d.variacao_total)}</td>
                        <td class="text-right"><span class="badge ${d.variacao_pct >= 0 ? 'positive' : 'negative'}">${fmtPct(d.variacao_pct)}</span></td>
                    </tr>
                `;
            })
            .catch(e => console.error("Erro ao carregar relatório:", e));
    </script>
</body>
</html>
"""

with open('../pc_frontend/relatorio_centro_custos.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] Relatório de Centro de Custos criado!")
