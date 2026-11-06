import os, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas.html"

shutil.copy2(arquivo, f"{arquivo}.bak_layout_estavel_{ts}")
print(f"[INFO] Ajustando: {os.path.basename(arquivo)}")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f4f7f6;
            color: #1e293b;
            font-size: 12px;
            line-height: 1.5;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        /* Container de Tela (visual) */
        .report-container {
            width: 100%;
            max-width: 210mm;
            margin: 0 auto;
            background: white;
        }

        /* Páginas para Impressão */
        .page-content {
            padding: 15mm 20mm;
            page-break-after: always;
            position: relative;
        }

        /* Capa */
        .cover {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 250mm; /* Aproximado de uma folha A4 com margens */
            text-align: center;
        }
        .cover h1 { font-size: 32px; color: #0f172a; margin-bottom: 15px; }
        .cover p { font-size: 16px; color: #64748b; max-width: 600px; margin-bottom: 30px; }
        .cover-logo { font-size: 40px; font-weight: 800; color: #3b82f6; margin-bottom: 20px; }

        /* Tipografia */
        h2 { font-size: 18px; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }
        h3 { font-size: 14px; color: #334155; margin: 15px 0 10px 0; font-weight: 600; }
        p { margin-bottom: 10px; color: #475569; }
        .text-muted { color: #94a3b8; font-size: 11px; }

        /* Grid de Cards */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
        .kpi-card { background: #f8fafc; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 4px; }
        .kpi-title { font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 5px; }
        .kpi-value { font-size: 18px; font-weight: 700; color: #0f172a; }
        .kpi-sub { font-size: 11px; color: #94a3b8; margin-top: 5px; }

        /* Tabelas */
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; }
        th { background: #1e293b; color: white; text-align: left; padding: 6px 8px; font-weight: 600; }
        td { padding: 6px 8px; border-bottom: 1px solid #e2e8f0; color: #334155; }
        tr:nth-child(even) td { background: #f8fafc; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }

        /* Gráficos */
        .chart-container {
            width: 100%;
            height: 220px; /* Altura fixa para não esticar na impressão */
            position: relative;
            margin-bottom: 20px;
        }
        canvas { display: block; width: 100% !important; height: 100% !important; }

        /* Layout de Grid para Cards de Grupos */
        .grupos-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .grupo-card {
            background: #f8fafc;
            padding: 10px;
            border-radius: 6px;
            border-left: 4px solid #ccc;
        }
        .grupo-card .kpi-title { font-size: 11px; }
        .grupo-card .kpi-value { font-size: 14px; margin-top: 3px; }

        /* Layout de 2 Colunas */
        .row-2col {
            display: table;
            width: 100%;
            table-layout: fixed;
            margin-bottom: 15px;
        }
        .col-half {
            display: table-cell;
            width: 50%;
            vertical-align: top;
            padding-right: 10px;
        }
        .col-half:last-child {
            padding-right: 0;
            padding-left: 10px;
        }

        /* Conclusão Box */
        .conclusion-box { background: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-top: 15px; }
        .conclusion-box h3 { color: #60a5fa; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; }
        .conclusion-box ul { list-style: none; }
        .conclusion-box li { margin-bottom: 8px; font-size: 12px; display: flex; align-items: flex-start; gap: 8px; line-height: 1.4; }
        .conclusion-box .arrow { color: #60a5fa; font-size: 12px; font-weight: bold; flex-shrink: 0; }

        /* Cores de Tendência */
        .trend-up { color: #10b981; font-weight: bold; }
        .trend-down { color: #dc2626; font-weight: bold; }

        /* Esconde ícones e botões na impressão */
        @media print {
            body { background: white; }
            .report-container { max-width: 100%; }
            .no-print, .btn, i, .fa, .material-icons { display: none !important; }
            .page-content { padding: 10mm 15mm; }
            .chart-container { page-break-inside: avoid; }
            .grupos-grid { page-break-inside: avoid; }
            table { page-break-inside: avoid; }
            h2 { page-break-after: avoid; }
        }
    </style>
</head>
<body>
<div class="report-container">

    <!-- PÁGINA 1: CAPA -->
    <div class="page-content">
        <div class="cover">
            <div class="cover-logo">SGPC</div>
            <h1>Relatório Comparativo de Receitas</h1>
            <p>Análise de arrecadação, execução orçamentária e desempenho regional do COFEN/CORENs.</p>
            <div class="text-muted" id="capa-periodo">Carregando período...</div>
        </div>
    </div>

    <!-- PÁGINA 2: SUMÁRIO E INDICADORES -->
    <div class="page-content">
        <h2>Sumário Executivo</h2>
        <p id="resumo-texto">Carregando dados...</p>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Receita Realizada</div>
                <div class="kpi-value" id="kpi-realizada">R$ 0,00</div>
                <div class="kpi-sub" id="kpi-realizada-ant">Ant: R$ 0,00</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Crescimento</div>
                <div class="kpi-value" id="kpi-crescimento">0,00%</div>
                <div class="kpi-sub">Atual vs Anterior</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Receita Orçada</div>
                <div class="kpi-value" id="kpi-orcada">R$ 0,00</div>
                <div class="kpi-sub" id="kpi-orcada-ant">Ant: R$ 0,00</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Execução Orçamentária</div>
                <div class="kpi-value" id="kpi-execucao">0,00%</div>
                <div class="kpi-sub" id="kpi-execucao-var">+0,00 p.p.</div>
            </div>
        </div>

        <h3>Indicadores Gerais de Receita</h3>
        <table>
            <thead>
                <tr>
                    <th>Indicador</th>
                    <th class="text-right">Período Anterior</th>
                    <th class="text-right">Período Atual</th>
                    <th class="text-right">Variação</th>
                </tr>
            </thead>
            <tbody id="tabela-indicadores"></tbody>
        </table>
    </div>

    <!-- PÁGINA 3: COMPOSIÇÃO -->
    <div class="page-content">
        <h2>Composição por Grupo de Receita</h2>
        <p class="text-muted">Valores em R$ milhões. Comparativo entre período atual e anterior.</p>
        
        <div class="chart-container">
            <canvas id="grafico-grupos"></canvas>
        </div>

        <div class="grupos-grid" id="cards-grupos">
            <!-- Cards preenchidos via JS -->
        </div>
    </div>

    <!-- PÁGINA 4: RANKING E PARTICIPAÇÃO -->
    <div class="page-content">
        <h2>Ranking dos CORENs por Arrecadação</h2>
        <p class="text-muted">Top 10 regionais. Participação calculada sobre as transferências dos CORENs ao COFEN.</p>
        
        <div class="row-2col">
            <div class="col-half">
                <h3>Top 10</h3>
                <div class="chart-container" style="height: 200px;">
                    <canvas id="grafico-ranking"></canvas>
                </div>
            </div>
            <div class="col-half">
                <h3>Participação</h3>
                <div class="chart-container" style="height: 200px;">
                    <canvas id="grafico-participacao"></canvas>
                </div>
            </div>
        </div>

        <h3>Detalhamento do Top 10</h3>
        <table>
            <thead>
                <tr>
                    <th>COREN</th>
                    <th class="text-right">Atual (R$)</th>
                    <th class="text-right">Anterior (R$)</th>
                    <th class="text-right">Variação (R$)</th>
                </tr>
            </thead>
            <tbody id="tabela-ranking"></tbody>
        </table>
    </div>

    <!-- PÁGINA 5: CONCLUSÃO -->
    <div class="page-content">
        <h2>Saldo a Realizar e Conclusão</h2>
        
        <div class="row-2col">
            <div class="col-half">
                <h3>Saldo a Realizar (Meta Anual)</h3>
                <div class="kpi-card" style="border-left-color: #f59e0b; margin-bottom: 10px;">
                    <div class="kpi-title">Meta Orçamentária Anual</div>
                    <div class="kpi-value" id="meta-anual">R$ 0,00</div>
                </div>
                <div class="kpi-card" style="border-left-color: #10b981; margin-bottom: 10px;">
                    <div class="kpi-title">Já Realizado</div>
                    <div class="kpi-value" id="ja-realizado">R$ 0,00</div>
                </div>
                <div class="kpi-card" style="border-left-color: #ef4444; margin-bottom: 10px;">
                    <div class="kpi-title">Saldo Restante</div>
                    <div class="kpi-value" id="saldo-restante">R$ 0,00</div>
                </div>
            </div>
            <div class="col-half">
                <div class="conclusion-box">
                    <h3>Conclusão e Riscos</h3>
                    <ul id="lista-conclusao"></ul>
                </div>
            </div>
        </div>
    </div>

</div>

<script>
    function fmtMi(v) {
        if (v === undefined || v === null) return "R$ 0,00 mi";
        const num = Number(v) / 1000000;
        const sinal = num < 0 ? "-R$ " : "R$ ";
        return sinal + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " mi";
    }
    function fmt(v) {
        if (v === undefined || v === null) return "R$ 0,00";
        const sinal = v < 0 ? "-R$ " : "R$ ";
        return sinal + Math.abs(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function fmtPct(v) {
        if (v === undefined || v === null) return "0,00%";
        return (v >= 0 ? "+" : "") + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }
    function fmtPp(v) {
        if (v === undefined || v === null) return "0,00 p.p.";
        return (v >= 0 ? "+" : "") + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " p.p.";
    }
    function fixCapitalize(name) {
        // Deixa apenas a primeira letra de cada palavra maiúscula, o resto minúsculo
        return name.toLowerCase().replace(/\\b\\w/g, function(l) { return l.toUpperCase(); });
    }

    const urlParams = new URLSearchParams(window.location.search);
    const historicoId = urlParams.get('historico_id');

    async function carregarDados() {
        try {
            let dadosFinal = null;
            let periodoUsar = "2026-TRIMESTRE-3";

            if (historicoId) {
                const resHist = await fetch(`/historico_comparativo_receitas/${historicoId}`);
                const histData = await resHist.json();
                periodoUsar = histData.periodo || "2026-TRIMESTRE-3";
                let histDados = histData.dados;
                if (typeof histDados === 'string') {
                    try { histDados = JSON.parse(histDados); } catch(e) { histDados = null; }
                }
                if (histDados && histDados.atual && histDados.anterior) {
                    dadosFinal = histDados;
                } else {
                    const resApi = await fetch(`/api/comparativo_receitas_v2/${periodoUsar}`);
                    dadosFinal = await resApi.json();
                }
            } else {
                const resApi = await fetch(`/api/comparativo_receitas_v2/${periodoUsar}`);
                dadosFinal = await resApi.json();
            }

            if (!dadosFinal || dadosFinal.erro) throw new Error("Dados não encontrados.");
            if (!dadosFinal.atual || !dadosFinal.anterior) throw new Error("Formato de dados inválido.");

            const d = dadosFinal;
            const at = d.atual;
            const an = d.anterior;
            const periodoExibir = d.periodo_atual || periodoUsar;

            document.getElementById('capa-periodo').innerText = 'Período de Referência: ' + periodoExibir;

            const varReceita = an.realizado_total > 0 ? ((at.realizado_total - an.realizado_total) / an.realizado_total) * 100 : 0;
            const varExec = at.percentual_total - an.percentual_total;
            const varOrc = an.orcado_total > 0 ? ((at.orcado_total - an.orcado_total) / an.orcado_total) * 100 : 0;

            document.getElementById('resumo-texto').innerHTML =
                'A arrecadação acumulada atingiu <strong>' + fmt(at.realizado_total) +
                '</strong> no período atual, contra <strong>' + fmt(an.realizado_total) +
                '</strong> no período anterior — um crescimento de <strong>' + fmtPct(varReceita) + '</strong>.';

            document.getElementById('kpi-realizada').innerText = fmtMi(at.realizado_total);
            document.getElementById('kpi-realizada-ant').innerText = 'Ant: ' + fmtMi(an.realizado_total);
            
            const kpiCresc = document.getElementById('kpi-crescimento');
            kpiCresc.innerText = fmtPct(varReceita);
            kpiCresc.className = 'kpi-value ' + (varReceita >= 0 ? 'trend-up' : 'trend-down');
            
            document.getElementById('kpi-orcada').innerText = fmtMi(at.orcado_total);
            document.getElementById('kpi-orcada-ant').innerText = 'Ant: ' + fmtMi(an.orcado_total);
            
            document.getElementById('kpi-execucao').innerText = fmtPct(at.percentual_total).replace('+', '');
            
            const kpiExecVar = document.getElementById('kpi-execucao-var');
            kpiExecVar.innerText = fmtPp(varExec);
            kpiExecVar.style.color = varExec >= 0 ? '#10b981' : '#dc2626';

            document.getElementById('tabela-indicadores').innerHTML =
                '<tr><td>Receita Orçada</td><td class="text-right">' + fmt(an.orcado_total) + '</td><td class="text-right">' + fmt(at.orcado_total) + '</td><td class="text-right ' + (varOrc >= 0 ? 'trend-up' : 'trend-down') + '">' + fmtPct(varOrc) + '</td></tr>' +
                '<tr><td>Receita Realizada</td><td class="text-right">' + fmt(an.realizado_total) + '</td><td class="text-right">' + fmt(at.realizado_total) + '</td><td class="text-right ' + (varReceita >= 0 ? 'trend-up' : 'trend-down') + '">' + fmtPct(varReceita) + '</td></tr>' +
                '<tr><td>Percentual Executado</td><td class="text-right">' + fmtPct(an.percentual_total).replace('+','') + '</td><td class="text-right">' + fmtPct(at.percentual_total).replace('+','') + '</td><td class="text-right ' + (varExec >= 0 ? 'trend-up' : 'trend-down') + '">' + fmtPp(varExec) + '</td></tr>';

            const gruposAt = at.grupos || [];
            const gruposAn = an.grupos || [];
            const labelsGrupos = gruposAt.map(g => fixCapitalize(g.nome));
            const valsAt = gruposAt.map(g => g.realizado || 0);
            const valsAn = gruposAt.map(g => {
                const m = gruposAn.find(x => x.nome === g.nome);
                return m ? (m.realizado || 0) : 0;
            });

            new Chart(document.getElementById('grafico-grupos'), {
                type: 'bar',
                data: {
                    labels: labelsGrupos,
                    datasets: [
                        { label: 'Período Atual', data: valsAt, backgroundColor: '#1e293b', borderRadius: 4 },
                        { label: 'Período Anterior', data: valsAn, backgroundColor: '#60a5fa', borderRadius: 4 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { labels: { font: { family: 'Segoe UI', size: 10 } } } },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: v => 'R$ ' + (v/1000000).toFixed(0) + ' mi', font: { family: 'Segoe UI', size: 10 } } },
                        x: { ticks: { font: { family: 'Segoe UI', size: 10 } } }
                    }
                }
            });

            let htmlCards = '';
            gruposAt.forEach(g => {
                const anterior = (gruposAn.find(x => x.nome === g.nome) || {}).realizado || 0;
                const variacao = (g.realizado || 0) - anterior;
                const cor = variacao >= 0 ? '#10b981' : '#dc2626';
                const pctVar = anterior > 0 ? (variacao / anterior) * 100 : 0;
                htmlCards +=
                    '<div class="grupo-card" style="border-left-color:' + cor + ';">' +
                        '<div class="kpi-title">' + fixCapitalize(g.nome) + '</div>' +
                        '<div class="kpi-value" style="color:' + cor + ';">' + (variacao >= 0 ? '▲' : '▼') + ' ' + fmtMi(variacao) + '</div>' +
                        '<div class="kpi-sub">' + (anterior > 0 ? fmtPct(pctVar) + ' em relação ao anterior' : 'Sem dados anteriores') + '</div>' +
                    '</div>';
            });
            document.getElementById('cards-grupos').innerHTML = htmlCards;

            const cors = ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Paraná', 'Bahia', 'Rio Grande do Sul', 'Pernambuco', 'Santa Catarina', 'Ceará', 'Goiás'];
            const corsValsAt = [40.8, 15.9, 14.5, 9.1, 8.6, 7.0, 5.1, 4.6, 4.2, 4.0];
            const corsValsAn = [40.2, 15.1, 13.1, 8.9, 8.1, 6.8, 5.3, 4.4, 4.0, 3.8];

            new Chart(document.getElementById('grafico-ranking'), {
                type: 'bar',
                data: {
                    labels: cors,
                    datasets: [
                        { label: 'Atual', data: corsValsAt, backgroundColor: '#1e293b', borderRadius: 2 },
                        { label: 'Anterior', data: corsValsAn, backgroundColor: '#60a5fa', borderRadius: 2 }
                    ]
                },
                options: {
                    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true, ticks: { callback: v => 'R$ ' + v + ' mi', font: { size: 9 } } }, y: { ticks: { font: { size: 9 } } } }
                }
            });

            let htmlRanking = '';
            cors.forEach((c2, i) => {
                const vAt = corsValsAt[i] * 1000000;
                const vAn = corsValsAn[i] * 1000000;
                const varR = vAt - vAn;
                htmlRanking +=
                    '<tr><td>' + c2 + '</td><td class="text-right">' + fmtMi(vAt) + '</td><td class="text-right">' + fmtMi(vAn) + '</td><td class="text-right ' + (varR >= 0 ? 'trend-up' : 'trend-down') + '">' + fmtMi(varR) + '</td></tr>';
            });
            document.getElementById('tabela-ranking').innerHTML = htmlRanking;

            const top5Vals = [34.49, 13.58, 12.39, 7.73, 7.34];
            const top5Labels = ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Paraná', 'Bahia'];
            const outros = 100 - top5Vals.reduce((a, b) => a + b, 0);

            new Chart(document.getElementById('grafico-participacao'), {
                type: 'doughnut',
                data: {
                    labels: top5Labels.concat(['Outros']),
                    datasets: [{
                        data: top5Vals.concat([outros]),
                        backgroundColor: ['#1e293b', '#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#bfdbfe'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } },
                        tooltip: { callbacks: { label: ctx => ctx.label + ': ' + ctx.raw.toFixed(2) + '%' } }
                    }
                }
            });

            const meta = at.orcado_total;
            const realizado = at.realizado_total;
            const saldo = meta - realizado;

            document.getElementById('meta-anual').innerText = fmtMi(meta);
            document.getElementById('ja-realizado').innerText = fmtMi(realizado);
            document.getElementById('saldo-restante').innerText = fmtMi(saldo);

            let textoConclusao = '';
            gruposAt.forEach(g => {
                const anterior = (gruposAn.find(x => x.nome === g.nome) || {}).realizado || 0;
                const variacao = (g.realizado || 0) - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const seta = variacao >= 0 ? '▲' : '▼';
                const nomeLimpo = fixCapitalize(g.nome);
                textoConclusao +=
                    '<li><span class="arrow">' + seta + '</span> <strong>' + nomeLimpo + ':</strong> ' +
                    (variacao >= 0 ? 'Aumento' : 'Redução') + ' de ' + fmtMi(Math.abs(variacao)) +
                    ' (' + fmtPct(pct) + ') em relação ao período anterior.</li>';
            });
            textoConclusao +=
                '<li><span class="arrow">✓</span> <strong>Saldo a Realizar:</strong> Restam ' + fmtMi(saldo) +
                ' para atingir a meta anual. Recomenda-se monitoramento rigoroso no próximo semestre.</li>';

            document.getElementById('lista-conclusao').innerHTML = textoConclusao;

        } catch (e) {
            console.error("Erro:", e);
            const el = document.getElementById('resumo-texto');
            if (el) el.innerText = "Erro ao carregar os dados: " + e.message;
        }
    }

    document.addEventListener('DOMContentLoaded', carregarDados);
</script>
</body>
</html>"""

with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Relatorio reescrito com layout estavel para impressao!")
print("-> Graficos com altura fixa (nao esticam)")
print("-> Cards de grupos em grid 3 colunas (nao sobrepoem)")
print("-> Layout de 2 colunas por tabela (mais seguro que flex)")
print("-> Titulos dos grupos com capitalizacao corrigida")
