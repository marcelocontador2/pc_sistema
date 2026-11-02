
(function() {
    // Cria o container mestre que vai segurar os cards
    const painel = document.createElement('div');
    painel.id = 'painel-integridade-novo';
    painel.style.display = 'none';
    painel.className = 'container mt-4';
    document.body.appendChild(painel);
    // Função que busca os dados e desenha
    async function carregarIntegridade(periodo) {
        painel.style.display = 'block';
        painel.innerHTML = '<div style="padding: 20px; color: #666;">Carregando análises de integridade...</div>';
        try {
            const res = await fetch(`/analise_integridade/${periodo}`);
            const data = await res.json();
            if (data.analises && data.analises.length > 0) {
                let html = '<h2 style="margin-bottom: 20px;">Análises de Integridade Contábil</h2>';
                data.analises.forEach(a => {
                    const cor = a.status === 'OK' ? '#28a745' : '#dc3545';
                    const icone = a.status === 'OK' ? '✅' : '❌';
                    html += `
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid ${cor};">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px;">
                            <h3 style="margin: 0; color: #333;">${a.titulo}</h3>
                            <span style="font-size: 1.5rem;">${icone}</span>
                        </div>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 20px;">${a.conceito}</p>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                            <tbody>
                                ${a.tabela.map(l => `
                                    <tr style="border-bottom: 1px solid #f0f0f0;">
                                        <td style="padding: 10px 0; color: #444;">${l.label}</td>
                                        <td style="padding: 10px 0; text-align: right; font-weight: bold; color: ${l.label.includes('Diferença') ? cor : '#333'};">${l.valor}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        <div style="background: ${a.status === 'OK' ? '#e8f5e9' : '#ffebee'}; color: ${cor}; padding: 12px; border-radius: 4px; font-weight: bold;">
                            ${a.mensagem}
                        </div>
                    </div>`;
                });
                painel.innerHTML = html;
            } else {
                painel.innerHTML = '<div style="padding: 20px; color: #d32f2f;">Nenhuma análise encontrada.</div>';
            }
        } catch (e) {
            console.error(e);
            painel.innerHTML = '<div style="padding: 20px; color: #d32f2f;">Erro ao carregar os dados do servidor.</div>';
        }
    }
    // Monitora mudanças no DOM (quando o seu sistema apaga a tela)
    const observer = new MutationObserver((mutations) => {
        // Procura o select de período na tela
        const selects = document.querySelectorAll('select');
        let periodoAtual = '';
        for (let i = 0; i < selects.length; i++) {
            if (selects[i].value && selects[i].value.includes('-')) {
                periodoAtual = selects[i].value;
                break;
            }
        }
        // Verifica se estamos na tela de integração
        const textoPagina = document.body.innerText || "";
        const isTelaIntegracao = textoPagina.includes("Integridade");
        if (isTelaIntegracao && periodoAtual && painel.style.display === 'none') {
            // Esconde os elementos antigos da tela para não ficar bagunçado
            const conteudoPrincipal = document.querySelector('main') || document.querySelector('.main-content') || document.querySelector('.content');
            if (conteudoPrincipal && !conteudoPrincipal.contains(painel)) {
                conteudoPrincipal.innerHTML = ''; // Limpa
                conteudoPrincipal.appendChild(painel); // Coloca o nosso painel
                painel.style.display = 'block';
                carregarIntegridade(periodoAtual);
            }
        }
    });
    // Começa a monitorar o body
    observer.observe(document.body, { childList: true, subtree: true });
    // Escuta mudança no select para carregar os dados
    document.body.addEventListener('change', function(e) {
        if (e.target.tagName === 'SELECT' && e.target.value.includes('-')) {
            const textoPagina = document.body.innerText || "";
            if (textoPagina.includes("Integridade")) {
                carregarIntegridade(e.target.value);
            }
        }
    });
})();
