import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_correcao_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove o lixo de caracteres que o Python está vendo no arquivo
c = re.sub(r'[\x80-\xff]{10,}', '', c)

# 2. Script "Dominó" que força o layout correto no DOM antes da impressão
script_fix = """
    <script id="fix_relatorio_pdf">
        (function() {
            // A. Remove textos que sejam lixo (caracteres estranhos)
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
            let node;
            while(node = walker.nextNode()) {
                if (node.nodeValue && /[\u0080-\u00FF]{5,}/.test(node.nodeValue)) {
                    node.nodeValue = ''; // Limpa o texto corrompido
                }
            }

            // B. Injeta o CSS de impressão forçado
            const style = document.createElement('style');
            style.innerHTML = `
                @media print {
                    /* Esconde botões, ícones quebrados e menus */
                    button, .btn, .no-print, i, .fa, .fas, .far, .material-icons, [class*="icon"] {
                        display: none !important;
                    }
                    
                    /* Força a grade 2x2 nos cards do sumário */
                    .cards-grid, .grid-kpis, .cards-container, .d-flex, .row {
                        display: grid !important;
                        grid-template-columns: 1fr 1fr !important;
                        gap: 20px !important;
                        page-break-inside: avoid !important;
                    }

                    /* Garante que os cards não vazem */
                    .card, .kpi-card {
                        width: 100% !important;
                        box-sizing: border-box !important;
                        padding: 15px !important;
                        page-break-inside: avoid !important;
                    }

                    /* Corrige o tamanho da fonte dos valores */
                    .card-value, .kpi-value {
                        font-size: 18px !important;
                        white-space: nowrap !important;
                    }
                }
            `;
            document.head.appendChild(style);

            // C. Injeta o espião para puxar os dados do histórico (se houver)
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('/api/relatorio_v2/')) {
                        return originalFetch(`/historico_centro_custos/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dados = data.dados ? data.dados : data;
                                const centros = dados.centros || [];
                                const centrosAnt = dados.centros_anterior || [];

                                const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
                                const totalAnterior = centrosAnt.reduce((acc, c) => acc + c.valor, 0);
                                const variacao_pct = totalAnterior > 0 ? ((totalAtual - totalAnterior) / totalAnterior) * 100 : 0;
                                
                                let maiorCentro = { nome: "Nenhum", valor: 0 };
                                if (centros.length > 0) {
                                    maiorCentro = centros.reduce((max, c) => c.valor > max.valor ? c : max, centros[0]);
                                }

                                const respostaFinal = {
                                    atual: { total: totalAtual, media_mensal: totalAtual / 9, maior_centro: maiorCentro },
                                    anterior: { total: totalAnterior, media_mensal: totalAnterior / 9 },
                                    variacao_pct: variacao_pct,
                                    centros: centros,
                                    centros_anterior: centrosAnt
                                };

                                return new Response(JSON.stringify(respostaFinal), { 
                                    headers: { 'Content-Type': 'application/json' } 
                                });
                            });
                    }
                    return originalFetch(url, options);
                };
            }
        })();
    </script>
"""

# Injeta o script no final do body
if '</body>' in c:
    c = c.replace('</body>', script_fix + '\n</body>', 1)
else:
    c += script_fix

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Script de formatação e limpeza injetado com sucesso!")
