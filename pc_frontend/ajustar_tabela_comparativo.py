c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Ajusta a função verificar() para chamar a API v2 (dados reais com comparativo)
c = c.replace(
    "const r = await fetch(`/api/comparativo_receitas/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });",
    "const r = await fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });"
)

# 2. Ajusta a função renderizarTabela para exibir o comparativo
antiga_render = """        function renderizarTabela(d) {
            let html = '<table><thead><tr><th>Centro de Receita</th><th>Valor (R$)</th><th>% do Total</th></tr></thead><tbody>';
            let total = 0;
            d.receitas.forEach(c => { total += c.valor; });
            d.receitas.forEach(c => {
                const pct = total > 0 ? (c.valor / total) * 100 : 0;
                html += `<tr><td>${c.nome}</td><td>${fmt(c.valor)}</td><td>${fmt(pct)}%</td></tr>`;
            });
            html += `<tr class="total-row"><td>TOTAL</td><td>${fmt(total)}</td><td>100%</td></tr></tbody></table>`;
            document.getElementById('tabela-container').innerHTML = html;
        }"""

nova_render = """        function renderizarTabela(d) {
            // A API v2 retorna d.atual (com grupos e cores) e d.anterior
            const gruposAt = d.atual.grupos || [];
            const gruposAn = d.anterior.grupos || [];
            
            // Filtra apenas os grupos com valores
            const grupos = gruposAt.filter(g => g.realizado > 0 || g.orcado > 0);
            const totalAtual = grupos.reduce((acc, g) => acc + g.realizado, 0);
            
            let html = '<table><thead><tr><th>Grupo de Receita</th><th>Período Atual (R$)</th><th>Período Anterior (R$)</th><th>Variação (R$)</th><th>Variação (%)</th></tr></thead><tbody>';
            
            grupos.forEach(g => {
                const anGrupo = gruposAn.find(x => x.nome === g.nome);
                const valorAnterior = anGrupo ? anGrupo.realizado : 0;
                const variacao = g.realizado - valorAnterior;
                const variacaoPct = valorAnterior > 0 ? (variacao / valorAnterior) * 100 : 0;
                const cor = variacao >= 0 ? '#dc3545' : '#28a745';
                
                html += `<tr>
                    <td>${g.nome}</td>
                    <td>${fmt(g.realizado)}</td>
                    <td>${fmt(valorAnterior)}</td>
                    <td style="color: ${cor};">${fmt(variacao)}</td>
                    <td style="color: ${cor};">${fmt(variacaoPct)}%</td>
                </tr>`;
            });
            
            const totalAnterior = gruposAn.reduce((acc, g) => acc + g.realizado, 0);
            const varTotal = totalAtual - totalAnterior;
            const varTotalPct = totalAnterior > 0 ? (varTotal / totalAnterior) * 100 : 0;
            const corTotal = varTotal >= 0 ? '#dc3545' : '#28a745';
            
            html += `<tr class="total-row">
                <td>TOTAL</td>
                <td>${fmt(totalAtual)}</td>
                <td>${fmt(totalAnterior)}</td>
                <td style="color: ${corTotal};">${fmt(varTotal)}</td>
                <td style="color: ${corTotal};">${fmt(varTotalPct)}%</td>
            </tr></tbody></table>`;
            
            document.getElementById('tabela-container').innerHTML = html;
        }"""

if antiga_render in c:
    c = c.replace(antiga_render, nova_render)
    print("[OK] Função renderizarTabela atualizada para comparativo!")
else:
    print("[AVISO] Função antiga não encontrada. Tentando regex...")
    import re
    padrao = r'function renderizarTabela\(d\) \{.*?\n        \}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, nova_render, c, flags=re.DOTALL)
        print("[OK] Função substituída via regex!")

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela atualizada com comparativo de períodos!")
