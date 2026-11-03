import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_calc_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove o espião antigo (que estava retornando os dados crus)
c = re.sub(r'<script id="interceptar_historico">.*?</script>', '', c, flags=re.DOTALL)

# Cria o novo espião inteligente, que calcula todos os campos que o relatório espera
novo_espiao = """
    <script id="interceptar_historico">
        (function() {
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

                                // 1. Calcular totais
                                const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
                                const totalAnterior = centrosAnt.reduce((acc, c) => acc + c.valor, 0);

                                // 2. Variação
                                const variacao = totalAtual - totalAnterior;
                                const variacao_pct = totalAnterior > 0 ? (variacao / totalAnterior) * 100 : 0;

                                // 3. Maior centro
                                let maiorCentro = { nome: "Nenhum", valor: 0 };
                                if (centros.length > 0) {
                                    maiorCentro = centros.reduce((max, c) => c.valor > max.valor ? c : max, centros[0]);
                                }

                                // 4. Montar objeto no formato que o relatório espera
                                const respostaFinal = {
                                    atual: {
                                        total: totalAtual,
                                        media_mensal: totalAtual / 3,
                                        maior_centro: maiorCentro
                                    },
                                    anterior: {
                                        total: totalAnterior,
                                        media_mensal: totalAnterior / 3
                                    },
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

# Injeta o novo espião no final da página (antes do </body>)
if '</body>' in c:
    c = c.replace('</body>', novo_espiao + '\n</body>', 1)
else:
    c += novo_espiao

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Espião inteligente injetado no relatório! Agora ele calcula todos os campos esperados.")
