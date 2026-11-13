c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Verifica se a página de conclusão já existe
if "Conclusão e Recomendações" not in c:
    nova_pagina = """
    <!-- CONCLUSÃO E RECOMENDAÇÕES -->
    <div class="page">
        <div class="section-subtitle">CONCLUSÃO</div>
        <h2 class="section-title">Conclusão e Recomendações</h2>
        
        <div style="display: flex; flex-direction: column; gap: 20px; margin-top: 20px;">
            
            <!-- Conclusão Principal -->
            <div style="background: var(--bg-light); padding: 25px; border-radius: 8px; border-left: 4px solid var(--primary);">
                <h3 style="color: var(--primary); margin-top: 0;">1. Conclusão sobre o Total Executado</h3>
                <p id="conclusao-total" style="font-size: 14px; line-height: 1.6;">
                    Carregando...
                </p>
            </div>

            <!-- Análise de Concentração -->
            <div style="background: var(--bg-light); padding: 25px; border-radius: 8px; border-left: 4px solid var(--secondary);">
                <h3 style="color: var(--primary); margin-top: 0;">2. Análise de Concentração</h3>
                <p id="conclusao-concentracao" style="font-size: 14px; line-height: 1.6;">
                    Carregando...
                </p>
            </div>

            <!-- Alertas e Pontos de Atenção -->
            <div style="background: #fff8e1; padding: 25px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h3 style="color: #856404; margin-top: 0;">3. Alertas e Pontos de Atenção</h3>
                <ul id="conclusao-alertas" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;">
                    <li>Carregando...</li>
                </ul>
            </div>

            <!-- Recomendações -->
            <div style="background: #d4edda; padding: 25px; border-radius: 8px; border-left: 4px solid #28a745;">
                <h3 style="color: #155724; margin-top: 0;">4. Recomendações</h3>
                <ul id="conclusao-recomendacoes" style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;">
                    <li>Carregando...</li>
                </ul>
            </div>

        </div>
    </div>
    """

    c = c.replace("</body>", nova_pagina + "\n</body>")
    print("[OK] Página de conclusão adicionada ao HTML!")
else:
    print("[AVISO] A página de conclusão já existe.")

# Adiciona o script que preenche a conclusão dinamicamente (no final do script existente)
if "preencherConclusao" not in c:
    script_conclusao = """
        function preencherConclusao(d) {
            // 1. Conclusão sobre o total
            const total = d.atual.total;
            const totalAnterior = d.anterior ? d.anterior.total : 0;
            const variacao = d.variacao_pct;
            const sinal = variacao >= 0 ? 'aumento' : 'redução';
            const cor = variacao >= 0 ? 'vermelho' : 'verde';
            
            document.getElementById('conclusao-total').innerHTML = `
                O total executado no período foi de <strong>R$ ${fmt(total)}</strong>, 
                o que representa um <strong style="color: ${variacao >= 0 ? '#dc3545' : '#28a745'};">${sinal} de ${fmtPct(Math.abs(variacao))}</strong> 
                em relação ao período anterior (R$ ${fmt(totalAnterior)}). 
                A média mensal de gastos foi de <strong>R$ ${fmt(d.atual.media_mensal)}</strong>.
            `;

            // 2. Concentração
            const centros = d.atual.centros.sort((a, b) => b.valor - a.valor);
            const top3 = centros.slice(0, 3);
            const somaTop3 = top3.reduce((acc, c) => acc + c.valor, 0);
            const pctTop3 = total > 0 ? (somaTop3 / total) * 100 : 0;
            const nomesTop3 = top3.map(c => c.nome).join(', ');
            
            document.getElementById('conclusao-concentracao').innerHTML = `
                Os <strong>3 maiores centros de custo</strong> (${nomesTop3}) 
                concentram <strong>${fmtPct(pctTop3)}</strong> do gasto total, 
                somando R$ ${fmt(somaTop3)}. Isso indica ${pctTop3 > 60 ? 'alta concentração' : 'distribuição equilibrada'} dos gastos.
            `;

            // 3. Alertas
            const alertas = [];
            if (variacao > 10) {
                alertas.push(`O gasto total cresceu ${fmtPct(variacao)} em relação ao período anterior, exigindo atenção.`);
            } else if (variacao < -10) {
                alertas.push(`O gasto total reduziu ${fmtPct(Math.abs(variacao))} em relação ao período anterior, o que é positivo.`);
            } else {
                alertas.push(`O gasto total manteve-se estável em relação ao período anterior (variação de ${fmtPct(variacao)}).`);
            }
            
            // Verifica se há centro com variação muito alta
            centros.forEach(c => {
                const anterior = d.anterior.centros.find(x => x.nome === c.nome);
                if (anterior && anterior.valor > 0) {
                    const varC = ((c.valor - anterior.valor) / anterior.valor) * 100;
                    if (varC > 50) {
                        alertas.push(`O centro "${c.nome}" teve um aumento de ${fmtPct(varC)} em relação ao período anterior.`);
                    }
                }
            });
            
            if (alertas.length === 0) {
                alertas.push("Não foram identificadas variações atípicas significativas.");
            }
            
            const ulAlertas = document.getElementById('conclusao-alertas');
            ulAlertas.innerHTML = alertas.map(a => `<li>${a}</li>`).join('');

            // 4. Recomendações
            const recomendacoes = [];
            if (pctTop3 > 60) {
                recomendacoes.push("Revisar os contratos e processos dos 3 maiores centros de custo, dado o alto grau de concentração.");
            }
            if (variacao > 10) {
                recomendacoes.push("Investigar as causas do aumento expressivo e implementar medidas de contenção.");
            }
            recomendacoes.push("Manter monitoramento mensal dos centros de custo para identificar desvios precocemente.");
            recomendacoes.push("Considerar a padronização de processos nos centros com maior variação.");
            
            const ulRecomendacoes = document.getElementById('conclusao-recomendacoes');
            ulRecomendacoes.innerHTML = recomendacoes.map(r => `<li>${r}</li>`).join('');
        }
    """
    
    # Adiciona a função antes do fechamento do script principal
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + script_conclusao + "\n" + c[pos:]
        print("[OK] Script de preenchimento da conclusão adicionado!")

    # Chama a função dentro do fetch principal
    c = c.replace(
        "// 3. Tabela de Composição",
        "// 3. Tabela de Composição\n                preencherConclusao(d);"
    )
    print("[OK] Chamada da função preencherConclusao adicionada!")

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado com a página de conclusão!")
