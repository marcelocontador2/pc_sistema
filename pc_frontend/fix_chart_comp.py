import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao renderChart no HTML
padrao = re.compile(r'function renderChart\(atual, anterior\)\s*\{.*?\n\}', re.DOTALL)

nova_render = '''function renderChart(atual, anterior) {
    const canvas = document.getElementById('graf');
    if (!canvas) return;

    // Verifica se o Chart.js carregou. Se nao, espera um pouco e tenta de novo.
    if (typeof Chart === 'undefined') {
        console.warn("Chart.js ainda nao carregou. Tentando novamente em 500ms...");
        setTimeout(function() { renderChart(atual, anterior); }, 500);
        return;
    }

    if (chart) { chart.destroy(); chart = null; }
    const labels = Object.keys(atual.receitas || {});
    const dataA = labels.map(k => atual.receitas[k] || 0);
    const dataB = labels.map(k => (anterior.receitas || {})[k] || 0);
    
    try {
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
    } catch (e) {
        console.error("Erro ao renderizar o grafico:", e);
    }
}'''

nova_s, n = padrao.subn(nova_render, s)

if n > 0:
    # Substitui tambem o catch do exibirSelecionado para nao dar alerta de erro se o grafico falhar
    # A ideia é separar o try/catch das tabelas do try/catch do gráfico
    padrao_exibir = re.compile(r'function exibirSelecionado\(\)\s*\{.*?\n\}', re.DOTALL)
    
    nova_exibir = '''function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    fetch('/historico_composicao_receitas_despesas/' + check.value)
        .then(r => { 
            if (!r.ok) throw new Error("Erro HTTP " + r.status); 
            return r.json(); 
        })
        .then(dados => {
            const atual = dados.atual || {};
            const anterior = dados.anterior || {};
            
            // 1. Renderiza as Tabelas (se der erro aqui, avisa)
            try {
                if (atual.receitas && anterior.receitas) renderTabela('tab-receitas', atual.receitas, anterior.receitas);
                if (atual.despesas && anterior.despesas) renderTabela('tab-despesas', atual.despesas, anterior.despesas);
            } catch (e) {
                console.error("Erro ao renderizar tabelas:", e);
            }
            
            // 2. Renderiza o Grafico (se der erro, só avisa no console, NAO trava a tela)
            try {
                renderChart(atual, anterior);
            } catch (e) {
                console.warn("O grafico nao pode ser carregado agora:", e.message);
            }
        })
        .catch(e => { 
            alert("Erro ao carregar histórico: " + e.message); 
            console.error(e); 
        });
}'''
    
    nova_s, n2 = padrao_exibir.subn(nova_exibir, nova_s)
    if n2 == 0:
        print("AVISO: Nao foi possivel substituir a funcao exibirSelecionado.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao renderChart melhorada (com retry) e exibirSelecionado separado em try/catch.")
else:
    print("AVISO: Nao foi possivel encontrar a funcao renderChart.")
