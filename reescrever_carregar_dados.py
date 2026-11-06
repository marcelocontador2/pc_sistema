import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_ordem_correta_{ts}")
c = open(arquivo, encoding='utf-8').read()

# ==========================================
# LOCALIZA A FUNÇÃO carregarDados INTEIRA
# ==========================================
inicio_func = c.find('async function carregarDados()')
if inicio_func == -1:
    print("[ERRO] Não encontrei a função carregarDados.")
    exit(1)

# Conta chaves para encontrar o fim da função
idx_chave = c.find('{', inicio_func)
nivel = 1
i = idx_chave + 1
while nivel > 0 and i < len(c):
    if c[i] == '{': nivel += 1
    elif c[i] == '}': nivel -= 1
    i += 1

fim_func = i

# ==========================================
# NOVA FUNÇÃO carregarDados COMPLETA, NA ORDEM CORRETA
# ==========================================
nova_func = """async function carregarDados() {
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

            if (!dadosFinal || dadosFinal.erro) throw new Error("Sem dados");
            if (!dadosFinal.atual || !dadosFinal.anterior) throw new Error("Formato inválido");

            const at = dadosFinal.atual;
            const an = dadosFinal.anterior;
            const periodoExibir = dadosFinal.periodo_atual || periodoUsar;

            document.getElementById('capa-periodo').innerText = 'Período: ' + periodoExibir;

            // ==========================================
            // KPIs DE TOPO
            // ==========================================
            const varReceita = an.realizado_total > 0 ? ((at.realizado_total - an.realizado_total) / an.realizado_total) * 100 : 0;
            const varExec = at.percentual_total - an.percentual_total;
            const varOrc = an.orcado_total > 0 ? ((at.orcado_total - an.orcado_total) / an.orcado_total) * 100 : 0;

            document.getElementById('resumo-texto').innerHTML = 
                'A arrecadação acumulada atingiu <strong>' + fmt(at.realizado_total) + 
                '</strong> no período atual, contra <strong>' + fmt(an.realizado_total) + 
                '</strong> no período anterior, um crescimento de <strong>' + fmtPct(varReceita) + '</strong>.';

            document.getElementById('kpi-realizada').innerText = fmtMi(at.realizado_total);
            document.getElementById('kpi-realizada-ant').innerText = 'Ant: ' + fmtMi(an.realizado_total);
            
            const kpiCresc = document.getElementById('kpi-crescimento');
            kpiCresc.innerText = fmtPct(varReceita);
            kpiCresc.style.color = varReceita >= 0 ? '#10b981' : '#dc2626';
            
            document.getElementById('kpi-orcada').innerText = fmtMi(at.orcado_total);
            document.getElementById('kpi-orcada-ant').innerText = 'Ant: ' + fmtMi(an.orcado_total);
            
            document.getElementById('kpi-execucao').innerText = fmt(at.percentual_total) + '%';
            
            const kpiExecVar = document.getElementById('kpi-execucao-var');
            kpiExecVar.innerText = fmtPp(varExec);
            kpiExecVar.style.color = varExec >= 0 ? '#10b981' : '#dc2626';

            document.getElementById('tabela-indicadores').innerHTML = 
                '<tr><td>Receita Orcada</td><td class="right">' + fmt(at.orcado_total) + '</td><td class="right">' + fmt(an.orcado_total) + '</td><td class="right ' + (varOrc >= 0 ? 'pos' : 'neg') + '">' + fmtPct(varOrc) + '</td></tr>' +
                '<tr><td>Receita Realizada</td><td class="right">' + fmt(at.realizado_total) + '</td><td class="right">' + fmt(an.realizado_total) + '</td><td class="right ' + (varReceita >= 0 ? 'pos' : 'neg') + '">' + fmtPct(varReceita) + '</td></tr>' +
                '<tr><td>Percentual Executado</td><td class="right">' + fmt(at.percentual_total) + '%</td><td class="right">' + fmt(an.percentual_total) + '%</td><td class="right ' + (varExec >= 0 ? 'pos' : 'neg') + '">' + fmtPp(varExec) + '</td></tr>';

            // ==========================================
            // DADOS DOS GRUPOS
            // ==========================================
            const gruposAt = at.grupos || [];
            const gruposAn = an.grupos || [];
            const labels = gruposAt.map(function(g) { return capitalizeNome(g.nome); });
            const valsAt = gruposAt.map(function(g) { return g.realizado || 0; });
            const valsAn = gruposAt.map(function(g) {
                const m = gruposAn.find(function(x) { return x.nome === g.nome; });
                return m ? (m.realizado || 0) : 0;
            });

            // ==========================================
            // GRÁFICO DE GRUPOS
            // ==========================================
            new Chart(document.getElementById('grafico-grupos'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Atual', data: valsAt, backgroundColor: '#1e293b' },
                        { label: 'Anterior', data: valsAn, backgroundColor: '#60a5fa' }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { font: { size: 10 } } }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + (v/1000000).toFixed(0) + ' mi'; }, font: { size: 9 } } },
                        x: { ticks: { font: { size: 9 } } }
                    }
                }
            });

            // ==========================================
            // CARDS DE GRUPOS
            // ==========================================
            let htmlGrupos = '';
            gruposAt.forEach(function(g) {
                const valorAtual = g.realizado || 0;
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
                const variacao = valorAtual - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const cor = variacao >= 0 ? '#10b981' : '#dc2626';
                const seta = variacao >= 0 ? '▲' : '▼';
                
                const txtAtual = fmt(valorAtual);
                const txtAnterior = anterior > 0 ? fmt(anterior) : '—';
                const txtVariacao = fmt(variacao);
                const txtPct = anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores';
                
                htmlGrupos += 
                    '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
                        '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
                        '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                            '<div style="font-size: 13px; color: #1e293b;">' +
                                '<strong>Recebido:</strong> ' + txtAtual +
                            '</div>' +
                            '<div style="font-size: 11px; color: #64748b;">' +
                                'Anterior: ' + txtAnterior +
                            '</div>' +
                        '</div>' +
                        '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' +
                            seta + ' ' + txtVariacao + ' (' + txtPct + ')' +
                        '</div>' +
                    '</div>';
            });
            
            const divGrupos = document.getElementById('lista-grupos');
            if (divGrupos) divGrupos.innerHTML = htmlGrupos;

            // ==========================================
            // RANKING TOP 10
            // ==========================================
            const cors = ['Sao Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Parana', 'Bahia', 'Rio Grande do Sul', 'Pernambuco', 'Santa Catarina', 'Ceara', 'Goias'];
            const corsAt = [40.8, 15.9, 14.5, 9.1, 8.6, 7.0, 5.1, 4.6, 4.2, 4.0];
            const corsAn = [40.2, 15.1, 13.1, 8.9, 8.1, 6.8, 5.3, 4.4, 4.0, 3.8];

            new Chart(document.getElementById('grafico-ranking'), {
                type: 'bar',
                data: {
                    labels: cors,
                    datasets: [
                        { label: 'Atual', data: corsAt, backgroundColor: '#1e293b' },
                        { label: 'Anterior', data: corsAn, backgroundColor: '#60a5fa' }
                    ]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + v + ' mi'; }, font: { size: 9 } } },
                        y: { ticks: { font: { size: 9 } } }
                    }
                }
            });

            let htmlRanking = '';
            cors.forEach(function(c2, i) {
                const vAt = corsAt[i] * 1000000;
                const vAn = corsAn[i] * 1000000;
                const varR = vAt - vAn;
                htmlRanking += 
                    '<tr><td>' + c2 + '</td><td class="right">' + fmtMi(vAt) + '</td><td class="right">' + fmtMi(vAn) + '</td><td class="right ' + (varR >= 0 ? 'pos' : 'neg') + '">' + fmtMi(varR) + '</td></tr>';
            });
            document.getElementById('tabela-ranking').innerHTML = htmlRanking;

            // ==========================================
            // PARTICIPAÇÃO (sem donut, texto)
            // ==========================================
            const top5Vals = [34.49, 13.58, 12.39, 7.73, 7.34];
            const top5Labels = ['Sao Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Parana', 'Bahia'];
            let htmlParticipacao = '<div style="font-weight: bold; margin-bottom: 8px;">Participação na Arrecadação</div>';
            top5Labels.forEach(function(l, i) {
                htmlParticipacao += '<div style="padding: 4px 0; border-bottom: 1px solid #e2e8f0;">' + 
                    l + ': <strong>' + top5Vals[i].toFixed(2) + '%</strong></div>';
            });
            htmlParticipacao += '<div style="padding: 4px 0;">Outros: <strong>' + (100 - top5Vals.reduce(function(a, b) { return a + b; }, 0)).toFixed(2) + '%</strong></div>';
            const divParticipacao = document.getElementById('participacao-info');
            if (divParticipacao) divParticipacao.innerHTML = htmlParticipacao;

            // ==========================================
            // SALDO A REALIZAR E CONCLUSÃO
            // ==========================================
            const meta = at.orcado_total;
            const realizado = at.realizado_total;
            const saldo = meta - realizado;

            document.getElementById('meta-anual').innerText = fmtMi(meta);
            document.getElementById('ja-realizado').innerText = fmtMi(realizado);
            document.getElementById('saldo-restante').innerText = fmtMi(saldo);

            let htmlConc = '';
            gruposAt.forEach(function(g) {
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
                const variacao = (g.realizado || 0) - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const seta = variacao >= 0 ? '▲' : '▼';
                htmlConc += 
                    '<div class="conclusao-linha">' +
                        seta + ' <strong>' + capitalizeNome(g.nome) + ':</strong> ' + 
                        (variacao >= 0 ? 'Aumento' : 'Reducao') + ' de ' + fmtMi(Math.abs(variacao)) + ' (' + fmtPct(pct) + ')' +
                    '</div>';
            });
            htmlConc += 
                '<div class="conclusao-linha">' +
                    '<strong>Saldo a Realizar:</strong> Restam ' + fmtMi(saldo) + ' para atingir a meta anual.' +
                '</div>';

            document.getElementById('lista-conclusao').innerHTML = htmlConc;

        } catch (e) {
            console.error("Erro:", e);
            document.getElementById('resumo-texto').innerText = 'Erro: ' + e.message;
        }
    }"""

c = c[:inicio_func] + nova_func + c[fim_func:]

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Função carregarDados reescrita NA ORDEM CORRETA!")
print("\n=== CORREÇÕES ===")
print("1. Variável 'cors' declarada ANTES de ser usada")
print("2. Cards de grupos na ordem correta")
print("3. Donut substituído por lista de participação em texto")
print("4. Saldo a Realizar e Conclusão no final")
