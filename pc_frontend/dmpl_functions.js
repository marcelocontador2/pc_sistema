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

function parseValorBrl(v) {
    if (typeof v === 'number') return isNaN(v) ? 0 : v;
    if (!v) return 0;
    var s = String(v).replace(/R\$/g, '').replace(/\s+/g, '').trim();
    if (!s || s === '-') return 0;
    if (s.indexOf(',') !== -1) {
        s = s.replace(/\./g, '').replace(',', '.');
    }
    var n = parseFloat(s);
    return isNaN(n) ? 0 : n;
}

function matrizParaLinhas(matriz) {
    if (!Array.isArray(matriz) || !matriz.length) return [];
    var saida = [];
    for (var i = 0; i < matriz.length; i++) {
        var row = matriz[i];
        if (!Array.isArray(row)) continue;
        var cols = row.map(function(c) { return (c === null || c === undefined) ? '' : String(c).trim(); });
        var naoVazios = cols.filter(function(c) { return c !== ''; });
        if (!naoVazios.length) continue;

        var desc = cols[0] || naoVazios[0] || '';
        var upper = desc.toUpperCase();
        if (upper.indexOf('CONSELHO FEDERAL') !== -1) continue;
        if (upper.indexOf('COFEN') !== -1) continue;
        if (upper.indexOf('CNPJ') !== -1) continue;
        if (upper.indexOf('DEMONSTRAÇÃO DAS MUTAÇÕES') !== -1 || upper.indexOf('DEMONSTRACAO DAS MUTACOES') !== -1) continue;
        if (upper.indexOf('PERÍODO:') === 0 || upper.indexOf('PERIODO:') === 0) continue;
        if (upper === 'PATRIMÔNIO SOCIAL E CAPITAL SOCIAL' && cols.indexOf('TOTAL') !== -1) continue;
        if (upper.indexOf('BRASÍLIA-DF') !== -1 || upper.indexOf('BRASILIA-DF') !== -1) continue;
        if (upper.indexOf('MARCELO RIBEIRO MEDEIROS') !== -1) continue;
        if (upper === 'CONTADOR') continue;
        if (upper.indexOf('CRC-') !== -1) continue;
        if (upper.indexOf('PÁGINA:') === 0 || upper.indexOf('PAGINA:') === 0) continue;

        var valores = [];
        for (var cIdx = 1; cIdx < cols.length; cIdx++) {
            valores.push(parseValorBrl(cols[cIdx]));
        }
        if (!valores.length) {
            valores = [parseValorBrl(naoVazios[naoVazios.length - 1])];
        }
        saida.push({ descricao: desc, valores: valores });
    }
    return saida;
}

function parseValorBrl(v) {
    if (typeof v === 'number') return isNaN(v) ? 0 : v;
    if (!v) return 0;
    var s = String(v).replace(/R\$/g, '').replace(/\s+/g, '').trim();
    if (!s || s === '-') return 0;
    if (s.indexOf(',') !== -1) {
        s = s.replace(/\./g, '').replace(',', '.');
    }
    var n = parseFloat(s);
    return isNaN(n) ? 0 : n;
}

function matrizParaLinhas(matriz) {
    if (!Array.isArray(matriz) || !matriz.length) return [];
    var saida = [];
    for (var i = 0; i < matriz.length; i++) {
        var row = matriz[i];
        if (!Array.isArray(row)) continue;
        var cols = row.map(function(c) { return (c === null || c === undefined) ? '' : String(c).trim(); });
        var naoVazios = cols.filter(function(c) { return c !== ''; });
        if (!naoVazios.length) continue;

        var desc = cols[0] || naoVazios[0] || '';
        var upper = desc.toUpperCase();
        if (upper.indexOf('CONSELHO FEDERAL') !== -1) continue;
        if (upper.indexOf('COFEN') !== -1) continue;
        if (upper.indexOf('CNPJ') !== -1) continue;
        if (upper.indexOf('DEMONSTRAÇÃO DAS MUTAÇÕES') !== -1 || upper.indexOf('DEMONSTRACAO DAS MUTACOES') !== -1) continue;
        if (upper.indexOf('PERÍODO:') === 0 || upper.indexOf('PERIODO:') === 0) continue;
        if (upper === 'PATRIMÔNIO SOCIAL E CAPITAL SOCIAL' && cols.indexOf('TOTAL') !== -1) continue;

        var valores = [];
        for (var cIdx = 1; cIdx < cols.length; cIdx++) {
            valores.push(parseValorBrl(cols[cIdx]));
        }
        if (!valores.length) {
            valores = [parseValorBrl(naoVazios[naoVazios.length - 1])];
        }
        saida.push({ descricao: desc, valores: valores });
    }
    return saida;
}

function movimentacoesParaLinhas(payload) {
    if (!payload || typeof payload !== 'object') return [];
    var saida = [];
    if (Array.isArray(payload.movimentacoes)) {
        payload.movimentacoes.forEach(function(m) {
            if (!m || typeof m !== 'object') return;
            var desc = m.especificacao || m.descricao || m.conta || m.movimentacao || '';
            if (!desc) return;
            var val = parseValorBrl(m.total !== undefined ? m.total : (m.valor !== undefined ? m.valor : 0));
            saida.push({ descricao: String(desc), valores: [val] });
        });
    }
    if (payload.resultado_periodo && typeof payload.resultado_periodo === 'object') {
        var resAtual = payload.resultado_periodo.atual;
        if (resAtual !== undefined && resAtual !== null) {
            saida.push({
                descricao: 'Resultado do Período (Atual)',
                valores: [parseValorBrl(resAtual)]
            });
        }
    }
    return saida;
}

function renderizarDados(dados) {
    var payload = dados;
    if (dados && dados.dados !== undefined) payload = dados.dados;
    if (payload && payload.dados !== undefined && !payload.linhas && !payload.movimentacoes) payload = payload.dados;

    var linhas = [];
    if (Array.isArray(payload)) {
        linhas = matrizParaLinhas(payload);
    } else if (payload && Array.isArray(payload.linhas)) {
        linhas = payload.linhas;
    } else if (payload && (Array.isArray(payload.movimentacoes) || payload.resultado_periodo)) {
        linhas = movimentacoesParaLinhas(payload);
    }

    var tbody = document.querySelector('#tab tbody') || document.querySelector('table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!linhas.length) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#999;">Nenhum dado para o periodo.</td></tr>';
        return;
    }

    var linhasFiltradas = linhas.filter(function(linha) {
        var desc = (linha.descricao || '').trim().toUpperCase();
        if (!desc) return false;
        if (desc.indexOf('COFEN') !== -1) return false;
        if (desc.indexOf('CNPJ') !== -1) return false;
        if (desc.indexOf('DEMONSTRA') !== -1) return false;
        if (desc.indexOf('BRASILIA') !== -1) return false;
        if (desc.indexOf('CONSELHO FEDERAL') !== -1) return false;
        if (desc.indexOf('BRASÍLIA-DF') !== -1 || desc.indexOf('BRASILIA-DF') !== -1) return false;
        if (desc.indexOf('MARCELO RIBEIRO MEDEIROS') !== -1) return false;
        if (desc === 'CONTADOR') return false;
        if (desc.indexOf('CRC-') !== -1) return false;
        if (desc.indexOf('PÁGINA:') === 0 || desc.indexOf('PAGINA:') === 0) return false;
        return true;
    });

    if (!linhasFiltradas.length) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#999;">Nenhum dado para o periodo.</td></tr>';
        return;
    }

    var totalGeral = 0;
    for (var i = linhasFiltradas.length - 1; i >= 0; i--) {
        var descUpper = (linhasFiltradas[i].descricao || '').toUpperCase();
        if (descUpper.indexOf('SALDOS FINAIS') !== -1 || descUpper.indexOf('TOTAL') !== -1) {
            var valsSaldos = linhasFiltradas[i].valores || [];
            var tSaldos = valsSaldos.length ? (valsSaldos[valsSaldos.length - 1] || 0) : 0;
            if (tSaldos !== 0) { totalGeral = tSaldos; break; }
        }
    }
    if (totalGeral === 0) {
        for (var j = linhasFiltradas.length - 1; j >= 0; j--) {
            var vals = linhasFiltradas[j].valores || [];
            var t = vals.length ? (vals[vals.length - 1] || 0) : 0;
            if (t !== 0) { totalGeral = t; break; }
        }
    }

    linhasFiltradas.forEach(function(linha) {
        var tr = document.createElement('tr');
        var desc = linha.descricao || '';
        var valores = linha.valores || [];
        var total = valores.length ? (valores[valores.length - 1] || 0) : 0;

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
    var checks = Array.prototype.slice.call(document.querySelectorAll('.hist-item input[type="checkbox"]:checked'));
    if (!checks.length) { alert('Selecione ao menos um item no historico.'); return; }
    var ids = checks.map(function(cb) { return parseInt(cb.value, 10); }).filter(function(n) { return !isNaN(n); });
    if (!ids.length) { alert('Nenhum ID valido selecionado.'); return; }

    var msg = ids.length === 1
        ? 'Deseja excluir o item selecionado do historico da DMPL?'
        : 'Deseja excluir os ' + ids.length + ' itens selecionados do historico da DMPL?';
    if (!confirm(msg)) return;

    fetch('/api/analise_dmpl/excluir_multiplos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: ids })
    })
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(function(j) {
            if (j && j.ok) {
                carregarHistorico();
            } else {
                alert('Erro ao excluir: ' + ((j && j.mensagem) || 'Falha desconhecida'));
            }
        })
        .catch(function(e) {
            console.error('[DMPL] Erro excluir_multiplos:', e);
            alert('Erro ao excluir itens: ' + e.message);
        });
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
