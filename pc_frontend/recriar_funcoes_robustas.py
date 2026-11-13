import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Remove a funcao carregar() antiga
padrao = re.compile(r'(async\s+)?function carregar\(\)\s*\{.*?\n\}', re.DOTALL)
js = padrao.sub('', js)

# 2. Adiciona a nova funcao carregar() robusta
nova_funcao = '''
function carregar() {
    const ano = document.getElementById('ano') ? document.getElementById('ano').value : '2026';
    const tipo = document.getElementById('tipo') ? document.getElementById('tipo').value : 'TRIMESTRE';
    const periodo = document.getElementById('periodo') ? document.getElementById('periodo').value : '3';
    
    const periodoFormatado = `${ano}-${tipo.toUpperCase()}-${periodo}`;
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    
    if(thead) {
        thead.innerHTML = '<th style="text-align:left;">Conta</th><th style="text-align:right;">Valor (R$)</th><th style="text-align:right;">% do Total</th>';
    }
    if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">Verificando...</td></tr>';

    fetch('/api/analise_dmpl/' + periodoFormatado)
        .then(response => {
            if (!response.ok) {
                // Se for erro HTTP (404, 500), tenta ler a mensagem JSON
                return response.json().then(err => {
                    throw new Error(err.mensagem || "Erro HTTP " + response.status);
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
            // Mostra a mensagem de erro na tabela, em vermelho
            if(tbody) {
                tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:#d9534f; font-weight:bold; padding:15px;">⚠️ ${error.message}</td></tr>`;
            }
            // Limpa o grafico
            if (window._chartDMPL) {
                window._chartDMPL.destroy();
                window._chartDMPL = null;
            }
        });
}
'''

# 3. Remove a funcao renderizarDados antiga (se existir) e recria
padrao_render = re.compile(r'function renderizarDados\(dados\)\s*\{.*?\n\}', re.DOTALL)
js = padrao_render.sub('', js)

nova_render = '''
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
        
        // Filtra cabecalhos
        if (!nome || 
            nome.includes('COFEN/BR') || 
            nome.includes('Conselho Federal') || 
            nome.includes('CNPJ') || 
            nome.includes('Demonstração') || 
            nome.includes('Período:') || 
            nome.includes('PATRIMÔNIO SOCIAL') ||
            nome.includes('Brasília-DF')) return;

        const vStr = (linha[8] || '0').trim();
        let vTotal = parseFloat(vStr.replace(/\\./g, '').replace(',', '.')) || 0;
        
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

    // Grafico
    if (window.Chart) {
        const canvas = document.getElementById('graf');
        if (canvas) {
            if (window._chartDMPL) window._chartDMPL.destroy();
            
            window._chartDMPL = new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Valor (R$)',
                        data: valores,
                        backgroundColor: '#0a1c3a'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }
    }
}
'''

js += nova_funcao + nova_render

with open(path, "w", encoding="utf-8") as f:
    f.write(js)
print("OK: Funcoes carregar() e renderizarDados() reescritas do zero com tratamento de erro na tabela!")
