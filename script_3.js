
// --- CARREGADOR DE RELATORIOS (Integracao com uploads_raw) ---
function carregarRelatorio(tipo) {
    // Esconde a tela de integridade se ela estiver aberta
    const overlay = document.getElementById('overlay-integridade');
    if (overlay) overlay.style.display = 'none';
    // Esconde todas as content-areas originais
    document.querySelectorAll('.content-area').forEach(e => e.classList.remove('active'));
    // Cria ou encontra a div de exibição do relatório
    let tela = document.getElementById('tela-relatorio-dinamico');
    if (!tela) {
        tela = document.createElement('div');
        tela.id = 'tela-relatorio-dinamico';
        tela.className = 'content-area active';
        tela.style.padding = '20px';
        // Insere no meio do layout principal (onde ficam os outros content-areas)
        const mainArea = document.querySelector('main') || document.querySelector('.main-content');
        if(mainArea) {
            mainArea.appendChild(tela);
        } else {
            document.body.appendChild(tela);
        }
    } else {
        tela.classList.add('active');
    }
    tela.innerHTML = '<h3 style="color:#0056b3;">Carregando ' + tipo + '...</h3>';
    // Busca os dados na rota do backend
    fetch('/api/ler_relatorio/' + tipo)
        .then(res => res.json())
        .then(data => {
            if (data.erro) {
                tela.innerHTML = '<p style="color:red;">' + data.erro + '</p>';
                return;
            }
            let html = '<h3 style="color:#0056b3;">Relatório: ' + data.tipo + '</h3>';
            html += '<p style="color:#666; margin-bottom: 15px;">Arquivo: ' + data.arquivo + '</p>';
            html += '<table class="tabela-relatorio">';
            data.dados.forEach((row, index) => {
                html += '<tr>';
                if (index === 0) {
                    row.forEach(cell => { html += '<th>' + cell + '</th>'; });
                } else {
                    row.forEach(cell => { html += '<td>' + cell + '</td>'; });
                }
                html += '</tr>';
            });
            html += '</table>';
            tela.innerHTML = html;
        })
        .catch(err => {
            tela.innerHTML = '<p style="color:red;">Erro ao buscar dados do servidor.</p>';
        });
}
// --- CONECTANDO OS BOTOES DO MENU ---
document.addEventListener("DOMContentLoaded", function() {
    // Mapeia os IDs dos menus para os tipos de arquivo
    const mapeamento = {
        'submenu-balancete': 'BALANCETE',
        'submenu-bp': 'BALANCO_PATRIMONIAL',
        'submenu-bo': 'BALANCO_ORCAMENTARIO',
        'submenu-bf': 'BALANCO_FINANCEIRO',
        'submenu-dfc': 'DFC',
        'submenu-dvp': 'DVP',
        'submenu-dmpl': 'DMPL'
    };
    for (const [id, tipo] of Object.entries(mapeamento)) {
        const link = document.getElementById(id);
        if (link) {
            // Sobrescreve apenas o onclick desses links específicos
            link.onclick = function(e) {
                e.preventDefault();
                carregarRelatorio(tipo);
            };
        }
    }
});
