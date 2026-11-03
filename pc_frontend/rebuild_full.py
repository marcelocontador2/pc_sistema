import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("analise_comparativo_despesas.html", f"analise_comparativo_despesas.html.bak_{ts}")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Comparativo de Despesas</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { font-size: 24px; margin-bottom: 5px; color: #1a202c; }
        .subtitle { color: #718096; margin-bottom: 20px; font-size: 14px; }
        .actions { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; color: #fff; font-weight: bold; font-size: 14px; }
        .btn-voltar { background: #ed8936; }
        .btn-exibir { background: #38a169; }
        .btn-excluir { background: #e53e3e; }
        .btn-pdf { background: #3182ce; }
        .btn-salvar { background: #38a169; }
        .btn-verificar { background: #3182ce; }
        .filters { display: flex; gap: 10px; align-items: center; background: #f7fafc; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .filters label { font-size: 14px; font-weight: 600; }
        .filters select { padding: 6px; border: 1px solid #cbd5e0; border-radius: 4px; }
        .historico-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin-bottom: 20px; }
        .historico-box h3 { font-size: 14px; color: #4a5568; margin-bottom: 10px; text-transform: uppercase; }
        .historico-box ul { list-style: none; padding: 0; margin: 0; }
        .historico-box li { padding: 8px 0; border-bottom: 1px solid #edf2f7; font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .card { background: #f8fafc; border-left: 4px solid #3182ce; padding: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card-title { font-size: 12px; font-weight: bold; color: #4a5568; text-transform: uppercase; margin-bottom: 5px; }
        .card-value { font-size: 22px; font-weight: bold; color: #1a202c; }
        .card-sub { font-size: 12px; color: #718096; margin-top: 5px; }
        table.data-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        table.data-table th, table.data-table td { padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        table.data-table th { background: #edf2f7; font-weight: bold; color: #2d3748; font-size: 13px; text-transform: uppercase; }
        .text-right { text-align: right; }
        .total-row td { font-weight: bold; background: #f7fafc; }
        .loading { color: #718096; font-size: 14px; padding: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Comparativo de Despesas</h1>
        <div class="subtitle">Apuração consolidada 12 meses</div>

        <div class="actions">
            <button class="btn btn-voltar" onclick="window.location.href='/'">← Voltar</button>
            <button class="btn btn-exibir" onclick="exibirSelecionado()">Exibir Selecionado</button>
            <button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>
            <button class="btn btn-pdf" onclick="window.print()">Gerar PDF</button>
            <button class="btn btn-salvar" onclick="salvarAtual()">Confirmar e Salvar</button>
        </div>

        <div class="historico-box">
            <h3>Histórico Salvo</h3>
            <div id="historico-lista" class="loading">Carregando histórico...</div>
        </div>

        <div class="filters">
            <label>Ano:</label>
            <select id="ano"><option value="2026" selected>2026</option><option value="2025">2025</option></select>
            <label>Tipo:</label>
            <select id="tipo"><option value="TRIMESTRE" selected>Trimestral</option><option value="MES">Mensal</option></select>
            <label>Período:</label>
            <select id="valor"><option value="1">1º</option><option value="2">2º</option><option value="3" selected>3º</option><option value="4">4º</option></select>
            <button class="btn btn-verificar" onclick="verificar()">Verificar</button>
        </div>

        <div class="cards-grid" id="cards-resumo">
            <div class="card">
                <div class="card-title">Despesa Orçada</div>
                <div class="card-value" id="resumo-orcado">R$ 0,00</div>
                <div class="card-sub" id="resumo-orcado-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card">
                <div class="card-title">Despesa Empenhada</div>
                <div class="card-value" id="resumo-empenhado">R$ 0,00</div>
                <div class="card-sub" id="resumo-empenhado-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card">
                <div class="card-title">Execução Orçamentária</div>
                <div class="card-value" id="resumo-execucao">0,00%</div>
                <div class="card-sub" id="resumo-execucao-delta">—</div>
            </div>
        </div>

        <div id="tabela-container"></div>
    </div>

    <script>
        let dadosAtuais = null;

        function fmt(v) {
            if (v === undefined || v === null || isNaN(v)) return '0,00';
            return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function atualizarCards(d) {
            const at = d.atual || {};
            const an = d.anterior || {};
            const varExec = (at.percentual_total || 0) - (an.percentual_total || 0);
            
            document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total);
            document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total);
            
            document.getElementById('resumo-empenhado').innerText = 'R$ ' + fmt(at.empenhado_total);
            document.getElementById('resumo-empenhado-anterior').innerText = 'Anterior: R$ ' + fmt(an.empenhado_total);
            
            document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total) + '%';
            
            const deltaEl = document.getElementById('resumo-execucao-delta');
            deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
            deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
        }

        function renderizarTabela(d) {
            const gruposAt = (d.atual && d.atual.grupos) ? d.atual.grupos : [];
            const gruposAn = (d.anterior && d.anterior.grupos) ? d.anterior.grupos : [];
            const grupos = gruposAt.filter(g => (g.empenhado || 0) > 0 || (g.orcado || 0) > 0);
            const totalAtual = grupos.reduce((acc, g) => acc + (g.empenhado || 0), 0);
            
            let html = '<table class="data-table"><thead><tr><th>Grupo de Despesa</th><th class="text-right">Período Atual (R$)</th><th class="text-right">Período Anterior (R$)</th><th class="text-right">Variação (R$)</th><th class="text-right">Variação (%)</th></tr></thead><tbody>';
            
            grupos.forEach(g => {
                const anGrupo = gruposAn.find(x => x.nome === g.nome);
                const valorAnterior = anGrupo ? (anGrupo.empenhado || 0) : 0;
                const variacao = (g.empenhado || 0) - valorAnterior;
                const variacaoPct = valorAnterior > 0 ? (variacao / valorAnterior) * 100 : 0;
                const cor = variacao >= 0 ? '#28a745' : '#dc3545';
                
                html += `<tr>
                    <td>${g.nome}</td>
                    <td class="text-right">${fmt(g.empenhado)}</td>
                    <td class="text-right">${fmt(valorAnterior)}</td>
                    <td class="text-right" style="color: ${cor};">${fmt(variacao)}</td>
                    <td class="text-right" style="color: ${cor};">${fmt(variacaoPct)}%</td>
                </tr>`;
            });
            
            const totalAnterior = gruposAn.reduce((acc, g) => acc + (g.empenhado || 0), 0);
            const varTotal = totalAtual - totalAnterior;
            const varTotalPct = totalAnterior > 0 ? (varTotal / totalAnterior) * 100 : 0;
            const corTotal = varTotal >= 0 ? '#28a745' : '#dc3545';
            
            html += `<tr class="total-row">
                <td>TOTAL</td>
                <td class="text-right">${fmt(totalAtual)}</td>
                <td class="text-right">${fmt(totalAnterior)}</td>
                <td class="text-right" style="color: ${corTotal};">${fmt(varTotal)}</td>
                <td class="text-right" style="color: ${corTotal};">${fmt(varTotalPct)}%</td>
            </tr></tbody></table>`;
            
            document.getElementById('tabela-container').innerHTML = html;
        }

        async function verificar() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo').value;
            const valor = document.getElementById('valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;

            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`);
                const data = await res.json();
                if (data.erro) { alert("Aviso: " + data.mensagem); return; }
                
                dadosAtuais = data;
                atualizarCards(data);
                renderizarTabela(data);
            } catch (e) {
                console.error("Erro ao buscar dados:", e);
                alert("Falha ao carregar os dados.");
            }
        }

        async function salvarAtual() {
            if (!dadosAtuais) { alert("Clique em Verificar antes de salvar."); return; }
            const periodo = dadosAtuais.periodo_atual;
            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodo}/salvar`, { method: 'POST' });
                const data = await res.json();
                if (data.erro) { alert(data.mensagem); return; }
                alert("Salvo com sucesso!");
                carregarHistorico();
            } catch (e) {
                alert("Erro ao salvar.");
            }
        }

        async function carregarHistorico() {
            try {
                const res = await fetch(`/historico_comparativo_despesas?_t=${Date.now()}`);
                const data = await res.json();
                const div = document.getElementById('historico-lista');
                if (data.length === 0) {
                    div.innerHTML = '<p style="color:#718096;font-size:13px;">Nenhum histórico.</p>';
                    return;
                }
                let html = '<ul>';
                data.forEach(item => {
                    html += `<li>
                        <input type="radio" name="historico" value="${item.id}">
                        <span><b>Período:</b> ${item.periodo} | <b>Gerado em:</b> ${item.data_geracao}</span>
                    </li>`;
                });
                html += '</ul>';
                div.innerHTML = html;
            } catch (e) {
                document.getElementById('historico-lista').innerHTML = 'Erro ao carregar.';
            }
        }

        async function exibirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            
            try {
                const res = await fetch(`/historico_comparativo_despesas/${sel.value}`);
                const data = await res.json();
                if (data.ok) {
                    dadosAtuais = data.dados;
                    atualizarCards(data.dados);
                    renderizarTabela(data.dados);
                } else {
                    alert("Erro ao carregar o histórico.");
                }
            } catch (e) {
                alert("Erro de conexão.");
            }
        }

        async function excluirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            if (!confirm("Tem certeza que deseja excluir este histórico?")) return;
            
            try {
                await fetch(`/historico_comparativo_despesas/${sel.value}`, { method: 'DELETE' });
                carregarHistorico();
            } catch (e) {
                alert("Erro ao excluir.");
            }
        }

        // Carrega o histórico ao abrir a página
        document.addEventListener('DOMContentLoaded', carregarHistorico);
    </script>
</body>
</html>"""

with open('analise_comparativo_despesas.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Tela reescrita com os botoes de regra de negocio e Historico!")
