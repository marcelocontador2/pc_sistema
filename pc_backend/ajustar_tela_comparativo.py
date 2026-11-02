c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Substitui o card único por dois cards (Atual e Anterior)
c = c.replace(
    '<div class="card-total">\n            <div class="label">Total Executado (Período Atual)</div>\n            <div class="value" id="total-atual">R$ 0,00</div>\n        </div>',
    '''<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div class="card-total">
                <div class="label">Total Executado (Período Atual)</div>
                <div class="value" id="total-atual">R$ 0,00</div>
            </div>
            <div class="card-total">
                <div class="label">Total Executado (Período Anterior)</div>
                <div class="value" id="total-anterior">R$ 0,00</div>
            </div>
            <div class="card-total">
                <div class="label">Variação Global</div>
                <div class="value" id="variacao-global">0,00%</div>
            </div>
        </div>'''
)

# 2. Atualiza a função verificar() para usar os dados do backend (atual e anterior)
c = c.replace(
    '''        async function verificar() {
            const ano = document.getElementById('filtro-ano').value;
            const tipo = document.getElementById('filtro-tipo').value;
            const trimestre = document.getElementById('filtro-trimestre').value;
            const periodo = `${ano}-${tipo}-${trimestre}`;
            
            try {
                document.getElementById('tabela-container').innerHTML = '<div style="text-align: center; padding: 20px; color: #888;">Verificando...</div>';
                const r = await fetch(`/api/centro_custos/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                
                if (d.erro) {
                    document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">' + d.mensagem + '</div>';
                    return;
                }
                dadosAtuais = d;
                renderizarTabela(d);
                atualizarCardTotal(d);
            } catch (e) {
                console.error(e);
                document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Erro ao verificar.</div>';
            }
        }''',
    '''        async function verificar() {
            const ano = document.getElementById('filtro-ano').value;
            const tipo = document.getElementById('filtro-tipo').value;
            const trimestre = document.getElementById('filtro-trimestre').value;
            const periodo = `${ano}-${tipo}-${trimestre}`;
            
            try {
                document.getElementById('tabela-container').innerHTML = '<div style="text-align: center; padding: 20px; color: #888;">Verificando...</div>';
                const r = await fetch(`/api/centro_custos/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                
                if (d.erro) {
                    document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">' + d.mensagem + '</div>';
                    return;
                }
                dadosAtuais = d;
                renderizarTabela(d);
                atualizarCards(d);
            } catch (e) {
                console.error(e);
                document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Erro ao verificar.</div>';
            }
        }'''
)

# 3. Atualiza a função renderizarTabela para incluir as colunas do período anterior e variação
c = c.replace(
    '''        function renderizarTabela(d) {
            let html = '<table>';
            html += '<thead><tr><th>Centro de Custo</th><th>Valor (R$)</th><th>% do Total</th></tr></thead>';
            html += '<tbody>';
            let total = 0;
            d.centros.forEach(c => { total += c.valor; });
            d.centros.forEach(c => {
                const pct = total > 0 ? (c.valor / total) * 100 : 0;
                html += `<tr><td>${c.nome}</td><td>${fmt(c.valor)}</td><td>${fmt(pct)}%</td></tr>`;
            });
            html += `<tr class="total-row"><td>TOTAL</td><td>${fmt(total)}</td><td>100%</td></tr>`;
            html += '</tbody></table>';
            document.getElementById('tabela-container').innerHTML = html;
        }''',
    '''        function renderizarTabela(d) {
            const centros = d.centros || [];
            const centrosAnterior = d.centros_anterior || [];
            const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
            
            // Mapa de centros anteriores por nome
            const mapaAnterior = {};
            centrosAnterior.forEach(c => { mapaAnterior[c.nome] = c.valor; });
            
            let html = '<table>';
            html += '<thead><tr><th>Centro de Custo</th><th>Valor Atual (R$)</th><th>Valor Anterior (R$)</th><th>Variação (R$)</th><th>Variação (%)</th></tr></thead>';
            html += '<tbody>';
            
            centros.forEach(c => {
                const anterior = mapaAnterior[c.nome] || 0;
                const variacao = c.valor - anterior;
                const variacaoPct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const cor = variacao >= 0 ? '#dc3545' : '#28a745';
                html += `<tr>
                    <td>${c.nome}</td>
                    <td>${fmt(c.valor)}</td>
                    <td>${fmt(anterior)}</td>
                    <td style="color: ${cor};">${fmt(variacao)}</td>
                    <td style="color: ${cor};">${fmt(variacaoPct)}%</td>
                </tr>`;
            });
            
            const totalAnterior = centrosAnterior.reduce((acc, c) => acc + c.valor, 0);
            const variacaoTotal = totalAtual - totalAnterior;
            const variacaoTotalPct = totalAnterior > 0 ? (variacaoTotal / totalAnterior) * 100 : 0;
            const corTotal = variacaoTotal >= 0 ? '#dc3545' : '#28a745';
            
            html += `<tr class="total-row">
                <td>TOTAL</td>
                <td>${fmt(totalAtual)}</td>
                <td>${fmt(totalAnterior)}</td>
                <td style="color: ${corTotal};">${fmt(variacaoTotal)}</td>
                <td style="color: ${corTotal};">${fmt(variacaoTotalPct)}%</td>
            </tr>`;
            html += '</tbody></table>';
            document.getElementById('tabela-container').innerHTML = html;
        }'''
)

# 4. Substitui atualizarCardTotal por atualizarCards
c = c.replace(
    '''        function atualizarCardTotal(d) {
            const total = d.centros.reduce((acc, c) => acc + c.valor, 0);
            document.getElementById('total-atual').innerText = 'R$ ' + fmt(total);
        }''',
    '''        function atualizarCards(d) {
            const totalAtual = d.centros.reduce((acc, c) => acc + c.valor, 0);
            const totalAnterior = (d.centros_anterior || []).reduce((acc, c) => acc + c.valor, 0);
            const variacao = totalAnterior > 0 ? ((totalAtual - totalAnterior) / totalAnterior) * 100 : 0;
            
            document.getElementById('total-atual').innerText = 'R$ ' + fmt(totalAtual);
            document.getElementById('total-anterior').innerText = 'R$ ' + fmt(totalAnterior);
            
            const variacaoEl = document.getElementById('variacao-global');
            variacaoEl.innerText = (variacao >= 0 ? '▲ ' : '▼ ') + fmt(Math.abs(variacao)) + '%';
            variacaoEl.style.color = variacao >= 0 ? '#dc3545' : '#28a745';
        }'''
)

# 5. Ajusta a função exibirSelecionado para usar renderizarTabela e atualizarCards
c = c.replace(
    '''        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            const r = await fetch('/historico_centro_custos/' + check.value);
            const d = await r.json();
            if (d.dados) { dadosAtuais = d.dados; renderizarTabela(d.dados); atualizarCardTotal(d.dados); }
        }''',
    '''        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            const r = await fetch('/historico_centro_custos/' + check.value);
            const d = await r.json();
            if (d.dados) {
                dadosAtuais = d.dados;
                // Como o histórico salvo só tem o período atual, usamos os dados atuais
                // e buscamos o comparativo da API
                const periodo = d.periodo || '2026-TRIMESTRE-3';
                const apiR = await fetch(`/api/centro_custos/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const apiD = await apiR.json();
                if (!apiD.erro) {
                    dadosAtuais = apiD;
                    renderizarTabela(apiD);
                    atualizarCards(apiD);
                } else {
                    renderizarTabela({centros: d.dados.centros, centros_anterior: []});
                    atualizarCards({centros: d.dados.centros, centros_anterior: []});
                }
            }
        }'''
)

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela de análise atualizada com comparativo de períodos!")
