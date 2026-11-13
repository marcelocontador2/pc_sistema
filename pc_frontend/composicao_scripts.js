
// ========== FUNCOES DA COMPOSICAO ==========
let chart = null;

function fmtV(v) { return (v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function pct(va, vb) { if (!vb || vb === 0) return '-'; const v = ((va - vb) / Math.abs(vb)) * 100; return (v >= 0 ? '+' : '') + v.toFixed(2).replace('.', ',') + '%'; }

function renderTabela(id, at, ant) {
    const tb = document.querySelector('#' + id + ' tbody');
    if (!tb) return;
    let html = '';
    Object.keys(at).forEach(function(k) {
        const va = at[k] || 0, vb = ant[k] || 0;
        const v = pct(va, vb);
        const cls = v.startsWith('-') ? 'neg' : 'pos';
        html += '<tr><td>' + k + '</td><td>' + fmtV(va) + '</td><td>' + fmtV(vb) + '</td><td class="' + cls + '">' + v + '</td></tr>';
    });
    tb.innerHTML = html;
}

function renderChart(atual, anterior) {
    const canvas = document.getElementById('graf');
    if (!canvas) return;
    if (chart) { chart.destroy(); chart = null; }
    const labels = Object.keys(atual.receitas || {});
    const dataA = labels.map(k => atual.receitas[k] || 0);
    const dataB = labels.map(k => (anterior.receitas || {})[k] || 0);
    chart = new Chart(canvas, {
        type: 'bar',
        data: { labels: labels, datasets: [
            { label: 'Período Atual', data: dataA, backgroundColor: '#003366', borderRadius: 4 },
            { label: 'Período Anterior', data: dataB, backgroundColor: '#4a90e2', borderRadius: 4 }
        ]},
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { title: { display: true, text: 'Composição de Receitas (R$ mil)', font: { size: 14, weight: 'bold' }, color: '#003366' }, legend: { position: 'bottom' } },
            scales: { y: { beginAtZero: true, grid: { color: '#eef2f7' } } }
        }
    });
}

function carregarHistorico() {
    fetch('/historico_composicao_receitas_despesas')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('historico-lista');
            if (!el) return;
            if (!data || data.length === 0) { el.innerHTML = '<li>Nenhum histórico.</li>'; return; }
            let html = '';
            data.forEach(item => {
                html += `<li><label><input type="checkbox" class="check-hist" value="${item.id}" style="margin-right:5px;"><strong>${item.periodo}</strong><br><small style="color:#666;">${item.data_geracao}</small></label></li>`;
            });
            el.innerHTML = html;
        })
        .catch(e => { console.error("Erro no historico:", e); const el = document.getElementById('historico-lista'); if (el) el.innerHTML = '<li>Erro ao carregar.</li>'; });
}

function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    fetch('/historico_composicao_receitas_despesas/' + check.value)
        .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(dados => {
            const atual = dados.atual || {};
            const anterior = dados.anterior || {};
            if (atual.receitas && anterior.receitas) renderTabela('tab-receitas', atual.receitas, anterior.receitas);
            if (atual.despesas && anterior.despesas) renderTabela('tab-despesas', atual.despesas, anterior.despesas);
            if (typeof renderChart === 'function') renderChart(atual, anterior);
        })
        .catch(e => { alert("Erro ao carregar histórico: " + e.message); console.error(e); });
}

function salvarComposicao() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    const pAtual = ano + '-' + tipo + '-' + val;
    const pAnterior = String(parseInt(ano) - 1) + '-' + tipo + '-' + val;
    fetch('/salvar_composicao_receitas_despesas/' + pAtual + '/' + pAnterior, { method: 'POST' })
        .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(res => { alert("Relatório salvo com sucesso!"); carregarHistorico(); })
        .catch(e => { alert("Erro ao salvar: " + e.message); console.error(e); });
}

document.addEventListener("DOMContentLoaded", function() {
    carregarHistorico();
    const btnExibir = document.getElementById('btn-exibir-composicao');
    if (btnExibir) btnExibir.addEventListener('click', exibirSelecionado);
    const btnSalvar = document.querySelector('button[onclick="salvarComposicao()"]');
    if (btnSalvar) { btnSalvar.removeAttribute('onclick'); btnSalvar.addEventListener('click', salvarComposicao); }
});
