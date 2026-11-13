c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Substitui o bloco do gráfico de tendência para incluir a tabela abaixo
trend_page_old = '''    <!-- GRÁFICO DE TENDÊNCIA -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div class="chart-container">
            <div class="chart-box">
                <canvas id="grafico-tendencia"></canvas>
            </div>
            <div class="leitura-box">
                <h3>LEITURA DO GRÁFICO</h3>
                <ul id="leitura-tendencia">
                    <li>Carregando...</li>
                </ul>
            </div>
        </div>
    </div>'''

trend_page_new = '''    <!-- GRÁFICO DE TENDÊNCIA -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div class="chart-container" style="margin-bottom: 30px;">
            <div class="chart-box" style="flex: 1.5;">
                <canvas id="grafico-tendencia"></canvas>
            </div>
            <div class="leitura-box" style="flex: 1;">
                <h3>LEITURA DO GRÁFICO</h3>
                <ul id="leitura-tendencia">
                    <li>Carregando...</li>
                </ul>
            </div>
        </div>
        
        <!-- NOVA TABELA DE VALORES MENSAIS -->
        <div class="table-container" style="margin-top: 20px;">
            <table>
                <thead>
                    <tr>
                        <th>Mês</th>
                        <th class="text-right">Total Atual (R$)</th>
                        <th class="text-right">Total Anterior (R$)</th>
                        <th class="text-right">Variação (R$)</th>
                        <th class="text-right">Variação (%)</th>
                    </tr>
                </thead>
                <tbody id="tabela-mensal"></tbody>
            </table>
        </div>
    </div>'''

if trend_page_old in c:
    c = c.replace(trend_page_old, trend_page_new)
    print("[OK] Tabela mensal adicionada ao HTML!")
else:
    print("[AVISO] Bloco do gráfico não encontrado. Tentando substituição flexível...")
    import re
    padrao = r'<!-- GRÁFICO DE TENDÊNCIA -->\s*<div class="page">.*?</div>\s*</div>\s*</div>'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, trend_page_new, c, flags=re.DOTALL)
        print("[OK] Tabela mensal adicionada via regex!")

# 2. Adiciona o JavaScript para preencher a tabela mensal
js_old = '''                // Leitura do Gráfico (dinâmica)'''

js_new = '''                // Tabela Mensal
                const tbodyMensal = document.getElementById('tabela-mensal');
                if (tbodyMensal) {
                    tbodyMensal.innerHTML = '';
                    meses.forEach(m => {
                        const at = d.atual.meses[m] || 0;
                        const an = (d.anterior.meses || {})[m] || 0;
                        const varM = at - an;
                        const varPctM = an > 0 ? (varM / an) * 100 : (at > 0 ? 100 : 0);
                        const badgeClassM = varM >= 0 ? 'positive' : 'negative';
                        tbodyMensal.innerHTML += `
                            <tr>
                                <td>${m}</td>
                                <td class="text-right">${fmt(at)}</td>
                                <td class="text-right">${fmt(an)}</td>
                                <td class="text-right">${fmt(varM)}</td>
                                <td class="text-right"><span class="badge ${badgeClassM}">${fmtPct(varPctM)}</span></td>
                            </tr>
                        `;
                    });
                    
                    const totalAtualMes = valoresAtual.reduce((a, b) => a + b, 0);
                    const totalAnteriorMes = valoresAnterior.reduce((a, b) => a + b, 0);
                    const varTotalMes = totalAtualMes - totalAnteriorMes;
                    const varTotalMesPct = totalAnteriorMes > 0 ? (varTotalMes / totalAnteriorMes) * 100 : 0;
                    tbodyMensal.innerHTML += `
                        <tr class="total-row">
                            <td>TOTAL</td>
                            <td class="text-right">${fmt(totalAtualMes)}</td>
                            <td class="text-right">${fmt(totalAnteriorMes)}</td>
                            <td class="text-right">${fmt(varTotalMes)}</td>
                            <td class="text-right"><span class="badge ${varTotalMes >= 0 ? 'positive' : 'negative'}">${fmtPct(varTotalMesPct)}</span></td>
                        </tr>
                    `;
                }

                // Leitura do Gráfico (dinâmica)'''

if js_old in c:
    c = c.replace(js_old, js_new)
    print("[OK] Script de preenchimento da tabela mensal adicionado!")
else:
    print("[AVISO] Trecho JavaScript não encontrado.")

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado!")
