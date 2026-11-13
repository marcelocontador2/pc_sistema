import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Verifica se a funcao carregar ja existe (para nao duplicar)
if "function carregar()" in js:
    print("A funcao carregar() ja existe no arquivo JS.")
else:
    # Adiciona a funcao carregar no final do arquivo
    nova_funcao_carregar = '''

function carregar() {
    // Pega os valores dos campos da tela
    const ano = document.getElementById('ano') ? document.getElementById('ano').value : '2026';
    const tipo = document.getElementById('tipo') ? document.getElementById('tipo').value : 'TRIMESTRE';
    const periodo = document.getElementById('periodo') ? document.getElementById('periodo').value : '3';
    
    // Monta o periodo no formato esperado pelo backend (ex: 2026-TRIMESTRE-3)
    const periodoFormatado = `${ano}-${tipo.toUpperCase()}-${periodo}`;
    
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    
    if(thead) {
        thead.innerHTML = '<th style="text-align:left;">Conta</th><th style="text-align:right;">Valor (R$)</th><th style="text-align:right;">% do Total</th>';
    }
    if(tbody) tbody.innerHTML = '<tr><td colspan="3">Verificando dados do CSV...</td></tr>';

    // Chama a API que le o CSV
    fetch('/api/analise_dmpl/' + periodoFormatado)
        .then(r => {
            if (!r.ok) throw new Error("Arquivo CSV nao encontrado para este periodo.");
            return r.json();
        })
        .then(retorno => {
            // O backend pode retornar { dados: [...] } ou uma lista direta
            let dados = retorno.dados || retorno;
            if (typeof dados === 'string') {
                try { dados = JSON.parse(dados); } catch(e) { dados = []; }
            }
            
            let html = '';
            let labels = [];
            let valores = [];
            let totalGeral = 0;

            let dadosProcessados = [];
            dados.forEach(linha => {
                if (!Array.isArray(linha)) return;
                const nome = (linha[0] || '').trim();
                
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

            if(tbody) tbody.innerHTML = html || '<tr><td colspan="3" style="text-align:center;">Nenhum dado válido encontrado no CSV.</td></tr>';

            // Renderiza o grafico
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
        })
        .catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:red;">${e.message}</td></tr>`;
        });
}
'''
    js += nova_funcao_carregar
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK: Funcao 'carregar()' adicionada ao dmpl_functions.js com sucesso!")
