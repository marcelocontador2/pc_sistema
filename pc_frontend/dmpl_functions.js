function carregarHistorico() {
    fetch('/historico_analise_dmpl')
        .then(r => r.json())
        .then(data => {
            const lista = document.getElementById('historico-lista');
            if (!lista) return;
            if (!data || data.length === 0) { lista.innerHTML = '<div style="padding:10px; color:#777;">Nenhum histórico.</div>'; return; }
            
            let html = '';
            data.forEach(item => {
                html += `<div class="hist-item" style="margin-bottom:8px;">
                    <input type="checkbox" value="${item.id}" class="check-hist" style="margin-right:8px;">
                    <span style="font-weight:bold; color:#0056b3;">${item.periodo}</span><br>
                    <span style="font-size:11px; color:#888;">Gerado em: ${item.data_geracao}</span>
                </div>`;
            });
            lista.innerHTML = html;
        })
        .catch(e => console.error("Erro no historico:", e));
}

function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico primeiro."); return; }
    
    const id = check.value;
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    
    if(thead) {
        thead.innerHTML = '<th style="text-align:left;">Conta</th><th style="text-align:right;">Valor (R$)</th><th style="text-align:right;">% do Total</th>';
    }
    
    if(tbody) tbody.innerHTML = '<tr><td colspan="3">Carregando dados...</td></tr>';

    fetch('/historico_analise_dmpl/' + id)
        .then(r => r.json())
        .then(item => {
            if (!item || item.erro) { alert("Histórico não encontrado."); return; }
            
            let dados = item.dados;
            if (typeof dados === 'string') {
                try { dados = JSON.parse(dados); } catch(e) { dados = []; }
            }
            
            renderizarDados(dados?.dados || dados || []);
        })
        .catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:red;">Erro ao carregar dados.</td></tr>';
        });
}



// Funcao central para montar a tabela e o grafico


document.addEventListener("DOMContentLoaded", () => {
    carregarHistorico();
});







function carregar() {
    const ano = document.getElementById('ano') ? document.getElementById('ano').value : '2026';
    const tipo = document.getElementById('tipo') ? document.getElementById('tipo').value : 'TRIMESTRE';
    const periodo = document.getElementById('periodo') ? document.getElementById('periodo').value : '3';
    
    const periodoFormatado = `${ano}-${tipo.toUpperCase()}-${periodo}`;
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    const aviso = document.getElementById('aviso-erro');

    // 1. Limpa a tela IMEDIATAMENTE (para nao mostrar dados antigos)
    if(thead) {
        thead.innerHTML = '<th style="text-align:left;">Conta</th><th style="text-align:right;">Valor (R$)</th><th style="text-align:right;">% do Total</th>';
    }
    if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">Buscando dados...</td></tr>';
    if(aviso) aviso.style.display = 'none'; // Esconde o aviso anterior
    if (window._chartDMPL) { window._chartDMPL.destroy(); window._chartDMPL = null; } // Limpa o grafico

    // 2. Busca os dados novos
    fetch('/api/analise_dmpl/' + periodoFormatado)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.mensagem || "Arquivo não encontrado para este período.");
                }).catch(() => {
                    throw new Error("Erro HTTP " + response.status);
                });
            }
            return response.json();
        })
        .then(retorno => {
            if (retorno && retorno.erro) {
                throw new Error(retorno.mensagem || "Nenhum dado encontrado.");
            }
            let dados = retorno.dados || retorno;
            if (typeof dados === 'string') {
                try { dados = JSON.parse(dados); } catch(e) { dados = []; }
            }
            renderizarDados(dados);
        })
        .catch(error => {
            console.error("Falha na verificacao:", error);
            
            // Mostra a div de aviso vermelha
            if(aviso) {
                aviso.style.display = 'block';
                aviso.innerHTML = "⚠️ <strong>Aviso:</strong> " + error.message + " (Período: " + periodoFormatado + ")";
            }
            
            // Limpa a tabela
            if(tbody) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
            }
        });
}

function renderizarDados(dados) {
    const tbody = document.querySelector('#tab tbody');
    let html = '';
    let labels = [];
    let valores = [];
    let totalGeral = 0;
    let dadosProcessados = [];

    dados.forEach(linha => {
        if (!Array.isArray(linha)) return;
        const nome = (linha[0] || '').trim();
        if (!nome || nome.includes('COFEN/BR') || nome.includes('Conselho Federal') || nome.includes('CNPJ') || nome.includes('Demonstração') || nome.includes('Período:') || nome.includes('PATRIMÔNIO SOCIAL') || nome.includes('Brasília-DF')) return;

        const vStr = (linha[8] || '0').trim();
        let vTotal = parseFloat(vStr.replace(/\./g, '').replace(',', '.')) || 0;
        
        dadosProcessados.push({ nome, valor: vTotal });
        totalGeral += Math.abs(vTotal);
    });

    dadosProcessados.forEach(item => {
        let percentual = totalGeral > 0 ? (Math.abs(item.valor) / totalGeral) * 100 : 0;
        let vFormatado = item.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        let pFormatado = percentual.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';

        html += `<tr>
            <td style="text-align:left;">${item.nome}</td>
            <td style="text-align:right;">${vFormatado}</td>
            <td style="text-align:right;">${pFormatado}</td>
        </tr>`;
        labels.push(item.nome);
        valores.push(item.valor);
    });

    if(tbody) tbody.innerHTML = html || '<tr><td colspan="3" style="text-align:center;">Nenhum dado válido encontrado.</td></tr>';

    if (window.Chart) {
        const canvas = document.getElementById('graf');
        if (canvas) {
            if (window._chartDMPL) window._chartDMPL.destroy();
            window._chartDMPL = new Chart(canvas, {
                type: 'bar',
                data: { labels: labels, datasets: [{ label: 'Valor (R$)', data: valores, backgroundColor: '#0a1c3a' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
            });
        }
    }
}
