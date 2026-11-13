import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui a funcao exibirSelecionado inteira
padrao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico primeiro."); return; }
    
    const id = check.value;
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    
    // Ajusta o cabecalho para 3 colunas
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
            
            const d = dados?.dados || dados || [];
            let html = '';
            let labels = [];
            let valores = [];
            let totalGeral = 0;

            // 1. Processa os dados e calcula o total absoluto para os percentuais
            let dadosProcessados = [];
            d.forEach(linha => {
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
                totalGeral += Math.abs(vTotal); // Soma os valores absolutos para achar o 100%
            });

            // 2. Monta o HTML e prepara o grafico
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

            // 3. Renderiza o grafico se a biblioteca Chart.js existir na pagina
            if (window.Chart) {
                const canvas = document.getElementById('graficoDMPL');
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
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                }
            }
        })
        .catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:red;">Erro ao carregar dados.</td></tr>';
        });
}'''

nova_js, n = padrao.subn(nova_funcao, js)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_js)
    print("OK: Funcao atualizada para remover coluna anterior, calcular % e grafico!")
else:
    print("AVISO: Funcao exibirSelecionado nao encontrada no arquivo JS.")
