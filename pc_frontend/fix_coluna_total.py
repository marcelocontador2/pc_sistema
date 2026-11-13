import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_coluna_total")

# Substitui a funcao exibirSelecionado inteira
padrao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)

nova_funcao = '''function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    const id = check.value;
    const tbody = document.querySelector('#tab tbody');
    if(tbody) tbody.innerHTML = '<tr><td colspan="4">Carregando...</td></tr>';

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
            let labelsGrafico = [];
            let valoresGrafico = [];

            d.forEach(linha => {
                if (!Array.isArray(linha)) return;
                const nome = (linha[0] || '').trim();
                
                // Filtra apenas linhas que sao contas reais (ignora cabecalhos)
                if (!nome || 
                    nome === 'COFEN/BR' ||
                    nome.includes('Conselho Federal') || 
                    nome.includes('CNPJ') || 
                    nome.includes('Demonstração') || 
                    nome.includes('Período:') || 
                    nome.includes('PATRIMÔNIO SOCIAL') ||
                    nome.includes('Brasília-DF')) return;

                // A coluna 8 e o TOTAL
                const valorTotalStr = (linha[8] || '0').trim();

                // Funcao para converter string BR para float
                const parseValor = (str) => {
                    if (!str) return 0;
                    return parseFloat(str.replace(/\\./g, '').replace(',', '.')) || 0;
                };

                const vTotal = parseValor(valorTotalStr);
                const fmt = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

                html += `<tr>
                    <td style="text-align:left;">${nome}</td>
                    <td style="text-align:right;">${fmt(vTotal)}</td>
                    <td style="text-align:right;">-</td>
                    <td style="text-align:right;">-</td>
                </tr>`;

                labelsGrafico.push(nome);
                valoresGrafico.push(vTotal);
            });

            if(tbody) tbody.innerHTML = html || '<tr><td colspan="4" style="text-align:center;">Nenhum dado válido encontrado.</td></tr>';

            // Renderiza o grafico (se o Chart.js estiver na pagina)
            if (window.Chart) {
                const canvas = document.getElementById('graficoDMPL') || document.getElementById('grafico') || document.querySelector('canvas');
                if (canvas) {
                    if (window._chartDMPL) window._chartDMPL.destroy();
                    
                    window._chartDMPL = new Chart(canvas, {
                        type: 'bar',
                        data: {
                            labels: labelsGrafico,
                            datasets: [
                                { label: 'Total (R$)', data: valoresGrafico, backgroundColor: '#0a1c3a' }
                            ]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { position: 'top' } }
                        }
                    });
                }
            }
        })
        .catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:red;">Erro ao carregar dados.</td></tr>';
        });
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao exibirSelecionado ajustada para ler a coluna TOTAL (indice 8)!")
else:
    print("AVISO: Funcao nao encontrada para substituir.")
