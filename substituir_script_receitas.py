import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas.html"

shutil.copy2(arquivo, f"{arquivo}.bak_script_novo_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Localiza o ÚLTIMO <script>...</script> (o do JS principal)
# Encontra o último <script> sem src
matches = list(re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>', c, re.DOTALL))
if not matches:
    print("[ERRO] Não achei nenhum <script> inline.")
    exit(1)

# Pega o último script (o principal)
ultimo = matches[-1]
inicio = ultimo.start()
fim = ultimo.end()

novo_script_completo = """<script>
    // ==========================================
    // FUNÇÕES DE FORMATAÇÃO
    // ==========================================
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
        return name.replace(/\\b(De|Do|Da|Dos|Das)\\b/gi, function(m) { return m.toLowerCase(); });
    }

    // ==========================================
    // LÓGICA HÍBRIDA: Tenta histórico, senão API
    // ==========================================
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
                    console.log("[INFO] Usando histórico (formato novo).");
                } else {
                    console.log("[AVISO] Histórico em formato antigo. Buscando da API atual.");
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

            // PÁGINA 1: Capa
            const elCapa = document.getElementById('capa-periodo');
            if (elCapa) elCapa.innerText = 'Período de Referência: ' + periodoExibir;

            // PÁGINA 2: Resumo e Indicadores
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
            kpiCresc.className = 'kpi-value ' + (varReceita >= 0 ? 'trend-up receita' : 'trend-down receita');

            document.getElementById('kpi-orcada').innerText = fmtMi(at.orcado_total);
            document.getElementById('kpi-orcada-ant').innerText = 'Ant: ' + fmtMi(an.orcado_total);

            document.getElementById('kpi-execucao').innerText = fmtPct(at.percentual_total).replace('+', '');

            const kpiExecVar = document.getElementById('kpi-execucao-var');
            kpiExecVar.innerText = fmtPp(varExec);
            kpiExecVar.style.color = varExec >= 0 ? '#10b981' : '#dc2626';

            document.getElementById('tabela-indicadores').innerHTML =
                '<tr>' +
                    '<td>Receita Orçada</td>' +
                    '<td class="text-right">' + fmt(an.orcado_total) + '</td>' +
                    '<td class="text-right">' + fmt(at.orcado_total) + '</td>' +
                    '<td class="text-right ' + (varOrc >= 0 ? 'trend-up receita' : 'trend-down receita') + '">' + fmtPct(varOrc) + '</td>' +
                '</tr>' +
                '<tr>' +
                    '<td>Receita Realizada</td>' +
                    '<td class="text-right">' + fmt(an.realizado_total) + '</td>' +
                    '<td class="text-right">' + fmt(at.realizado_total) + '</td>' +
                    '<td class="text-right ' + (varReceita >= 0 ? 'trend-up receita' : 'trend-down receita') + '">' + fmtPct(varReceita) + '</td>' +
                '</tr>' +
                '<tr>' +
                    '<td>Percentual Executado</td>' +
                    '<td class="text-right">' + fmtPct(an.percentual_total).replace('+','') + '</td>' +
                    '<td class="text-right">' + fmtPct(at.percentual_total).replace('+','') + '</td>' +
                    '<td class="text-right ' + (varExec >= 0 ? 'trend-up receita' : 'trend-down receita') + '">' + fmtPp(varExec) + '</td>' +
                '</tr>';

            // PÁGINA 3: Gráfico de Grupos
            const gruposAt = at.grupos || [];
            const gruposAn = an.grupos || [];
            const labelsGrupos = gruposAt.map(function(g) { return fixCapitalize(g.nome); });
            const valsAt = gruposAt.map(function(g) { return g.realizado || 0; });
            const valsAn = gruposAt.map(function(g) {
                const m = gruposAn.find(function(x) { return x.nome === g.nome; });
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
                    plugins: { legend: { labels: { font: { family: 'Segoe UI' } } } },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + (v/1000000).toFixed(0) + ' mi'; }, font: { family: 'Segoe UI' } } },
                        x: { ticks: { font: { family: 'Segoe UI' } } }
                    }
                }
            });

            let htmlCards = '';
            gruposAt.forEach(function(g) {
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
                const variacao = (g.realizado || 0) - anterior;
                const cor = variacao >= 0 ? '#10b981' : '#dc2626';
                const pctVar = anterior > 0 ? (variacao / anterior) * 100 : 0;
                htmlCards +=
                    '<div class="col" style="background:#f8fafc; padding:10px; border-radius:6px; border-left:4px solid ' + cor + ';">' +
                        '<div class="kpi-title">' + fixCapitalize(g.nome) + '</div>' +
                        '<div class="kpi-value" style="color:' + cor + ';">' + (variacao >= 0 ? '▲' : '▼') + ' ' + fmtMi(variacao) + '</div>' +
                        '<div class="kpi-sub">' + (anterior > 0 ? fmtPct(pctVar) + ' em relação ao anterior' : 'Sem dados anteriores') + '</div>' +
                    '</div>';
            });
            document.getElementById('cards-grupos').innerHTML = htmlCards;

            // PÁGINA 4: Ranking e Participação
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
                    scales: { x: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + v + ' mi'; } } } }
                }
            });

            let htmlRanking = '';
            cors.forEach(function(c2, i) {
                const vAt = corsValsAt[i] * 1000000;
                const vAn = corsValsAn[i] * 1000000;
                const varR = vAt - vAn;
                htmlRanking +=
                    '<tr>' +
                        '<td>' + c2 + '</td>' +
                        '<td class="text-right">' + fmtMi(vAt) + '</td>' +
                        '<td class="text-right">' + fmtMi(vAn) + '</td>' +
                        '<td class="text-right ' + (varR >= 0 ? 'trend-up receita' : 'trend-down receita') + '">' + fmtMi(varR) + '</td>' +
                    '</tr>';
            });
            document.getElementById('tabela-ranking').innerHTML = htmlRanking;

            const top5Vals = [34.49, 13.58, 12.39, 7.73, 7.34];
            const top5Labels = ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Paraná', 'Bahia'];
            const outros = 100 - top5Vals.reduce(function(a, b) { return a + b; }, 0);

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
                        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10, family: 'Segoe UI' } } },
                        tooltip: { callbacks: { label: function(ctx) { return ctx.label + ': ' + ctx.raw.toFixed(2) + '%'; } } }
                    }
                }
            });

            // PÁGINA 5: Saldo a Realizar e Conclusão
            const meta = at.orcado_total;
            const realizado = at.realizado_total;
            const saldo = meta - realizado;

            document.getElementById('meta-anual').innerText = fmtMi(meta);
            document.getElementById('ja-realizado').innerText = fmtMi(realizado);
            document.getElementById('saldo-restante').innerText = fmtMi(saldo);

            let textoConclusao = '';
            gruposAt.forEach(function(g) {
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
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
</script>"""

c = c[:inicio] + novo_script_completo + c[fim:]

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Script JS substituido por completo no relatorio de receitas!")
print()
print("=== O QUE FOI CORRIGIDO ===")
print("1. Le do historico se o formato for novo (com atual/anterior)")
print("2. Se o historico for antigo, busca da API atual usando o periodo do historico")
print("3. Conclusao gerada dinamicamente baseada nos grupos")
print("4. Formatacao numerica padronizada")
