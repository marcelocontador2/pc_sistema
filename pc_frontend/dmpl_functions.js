// ============================================================
// Funções do DMPL (sobrescreve as originais)
// ============================================================
console.log('[DMPL] Carregando funcoes...');

function carregar() {
    var ano = document.getElementById('ano') ? document.getElementById('ano').value : '2026';
    var tipo = document.getElementById('tipo') ? document.getElementById('tipo').value : 'TRIMESTRE';
    var val = document.getElementById('val') ? document.getElementById('val').value : '3';
    var periodo = ano + '-' + tipo + '-' + val;
    console.log('[DMPL] Carregando periodo:', periodo);

    fetch('/api/analise_dmpl/' + periodo)
        .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function(data) {
            if (data.erro) {
                document.querySelector('#tab tbody').innerHTML = '<tr><td colspan="3" style="color:red;text-align:center;">' + (data.mensagem || 'CSV nao encontrado') + '</td></tr>';
                return;
            }
            renderizarDados(data);
            var btn = document.getElementById('btn-salvar');
            if (btn) {
                btn.style.display = 'inline-block';
                btn.setAttribute('data-periodo', periodo);
            }
        })
        .catch(function(e) {
            console.error('[DMPL] Erro:', e);
            document.querySelector('#tab tbody').innerHTML = '<tr><td colspan="3" style="color:red;text-align:center;">Erro: ' + e.message + '</td></tr>';
        });
}

function renderizarDados(dados) {
    var payload = dados;
    if (dados && dados.dados && dados.dados.linhas) payload = dados.dados;
    else if (dados && dados.linhas) payload = dados;

    var linhas = payload.linhas || [];
    var tbody = document.querySelector('#tab tbody') || document.querySelector('table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!linhas.length) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#999;">Nenhum dado para o periodo.</td></tr>';
        return;
    }

    // Encontra o total geral (última linha com valor não zero)
    var totalGeral = 0;
    for (var i = linhas.length - 1; i >= 0; i--) {
        var vals = linhas[i].valores || [];
        var t = vals[vals.length - 1] || 0;
        if (t !== 0) { totalGeral = t; break; }
    }

    linhas.forEach(function(linha) {
        var tr = document.createElement('tr');
        var desc = linha.descricao || '';
        var valores = linha.valores || [];
        var total = valores[valores.length - 1] || 0;

        var negrito = desc.toLowerCase().indexOf('saldos') !== -1 ||
                      desc.toLowerCase().indexOf('resultado') !== -1 ||
                      desc.toLowerCase().indexOf('total') !== -1;
        if (negrito) tr.style.fontWeight = 'bold';

        var tdDesc = document.createElement('td');
        tdDesc.innerText = desc;
        tr.appendChild(tdDesc);

        var tdValor = document.createElement('td');
        tdValor.className = 'right';
        tdValor.innerText = 'R$ ' + (total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        tr.appendChild(tdValor);

        var tdPct = document.createElement('td');
        tdPct.className = 'right';
        if (totalGeral !== 0 && total !== 0) {
            var pct = (total / totalGeral) * 100;
            tdPct.innerText = pct.toFixed(2).replace('.', ',') + '%';
            tdPct.className += pct >= 0 ? ' pos' : ' neg';
        } else {
            tdPct.innerText = '-';
        }
        tr.appendChild(tdPct);

        tbody.appendChild(tr);
    });
}

function carregarHistorico() {
    fetch('/api/analise_dmpl/historico')
        .then(function(r) { return r.json(); })
        .then(function(hist) {
            var div = document.getElementById('historico-lista');
            if (!div) return;
            div.innerHTML = '';
            if (!hist.length) {
                div.innerHTML = '<p style="font-size:13px;color:#999;">Nenhum historico.</p>';
                return;
            }
            hist.forEach(function(h) {
                var d = document.createElement('div');
                d.className = 'hist-item';
                d.innerHTML = '<input type="checkbox" value="' + h.id + '"> <span>' + h.periodo + '</span>';
                div.appendChild(d);
            });
        })
        .catch(function(e) { console.error('[DMPL] Erro historico:', e); });
}

function exibirSelecionado() {
    var sel = document.querySelector('.hist-item input:checked');
    if (!sel) { alert('Selecione um item no historico.'); return; }
    fetch('/api/analise_dmpl/historico/' + sel.value)
        .then(function(r) { return r.json(); })
        .then(function(j) { if (j.dados) renderizarDados({dados: j.dados}); });
}

function salvar() {
    var btn = document.getElementById('btn-salvar');
    var periodo = btn ? btn.getAttribute('data-periodo') : null;
    if (!periodo) { alert('Verifique os dados primeiro.'); return; }
    var partes = periodo.split('-');
    var anterior = (parseInt(partes[0]) - 1) + '-' + partes[1] + '-' + partes[2];
    fetch('/api/analise_dmpl/salvar/' + periodo + '/' + anterior, { method: 'POST' })
        .then(function(r) { return r.json(); })
        .then(function(j) { if (j.ok) { alert('Salvo com ID ' + j.id); carregarHistorico(); } else alert('Erro: ' + j.mensagem); });
}

function excluirSelecionado() {
    var sel = document.querySelector('.hist-item input:checked');
    if (!sel) { alert('Selecione um item.'); return; }
    if (!confirm('Excluir?')) return;
    fetch('/api/analise_dmpl/excluir/' + sel.value, { method: 'DELETE' })
        .then(function(r) { return r.json(); })
        .then(function(j) { if (j.ok) carregarHistorico(); });
}

function gerarPDF() {
    var sel = document.querySelector('.hist-item input:checked');
    if (!sel) { alert('Selecione um item no historico.'); return; }
    window.open('/api/analise_dmpl/gerar_pdf/' + sel.value, '_blank');
}

// Auto-load por ?id=
(function() {
    var params = new URLSearchParams(window.location.search);
    var id = params.get('id');
    if (!id) return;
    console.log('[DMPL-AUTO] Carregando id=' + id);
    fetch('/api/analise_dmpl/historico/' + id)
        .then(function(r) { return r.json(); })
        .then(function(j) { if (j.dados) renderizarDados({dados: j.dados}); });
})();

// Carrega historico ao abrir
document.addEventListener('DOMContentLoaded', carregarHistorico);
