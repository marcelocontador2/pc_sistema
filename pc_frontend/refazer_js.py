import re, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("analise_comparativo_despesas.html", f"analise_comparativo_despesas.html.bak_{ts}")
c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

c = re.sub(r'function fmt\(.*?\) \{.*?\}', '''function fmt(v) {
        if (v === undefined || v === null || isNaN(v)) return '0,00';
        return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }''', c, flags=re.DOTALL)

c = re.sub(r'function atualizarCards\(d\) \{.*?\}', '''function atualizarCards(d) {
        const at = d.atual || {};
        const an = d.anterior || {};
        const varExec = (at.percentual_total || 0) - (an.percentual_total || 0);
        
        document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total);
        document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total);
        
        document.getElementById('resumo-empenhado').innerText = 'R$ ' + fmt(at.empenhado_total);
        document.getElementById('resumo-empenhado-anterior').innerText = 'Anterior: R$ ' + fmt(an.empenhado_total);
        
        document.getElementById('resumo-liquidado').innerText = 'R$ ' + fmt(at.liquidado_total);
        document.getElementById('resumo-liquidado-anterior').innerText = 'Anterior: R$ ' + fmt(an.liquidado_total);
        
        document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total) + '%';
        const deltaEl = document.getElementById('resumo-execucao-delta');
        deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
        deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
    }''', c, flags=re.DOTALL)

c = re.sub(r'function renderizarTabela\(d\) \{.*?\}', '''function renderizarTabela(d) {
        const gruposAt = (d.atual && d.atual.grupos) ? d.atual.grupos : [];
        const gruposAn = (d.anterior && d.anterior.grupos) ? d.anterior.grupos : [];
        const grupos = gruposAt.filter(g => (g.empenhado || 0) > 0 || (g.orcado || 0) > 0);
        const totalAtual = grupos.reduce((acc, g) => acc + (g.empenhado || 0), 0);
        
        let html = '<table><thead><tr><th>Grupo de Despesa</th><th class="text-right">Período Atual (R$)</th><th class="text-right">Período Anterior (R$)</th><th class="text-right">Variação (R$)</th><th class="text-right">Variação (%)</th></tr></thead><tbody>';
        
        grupos.forEach(g => {
            const anGrupo = gruposAn.find(x => x.nome === g.nome);
            const valorAnterior = anGrupo ? (anGrupo.empenhado || 0) : 0;
            const variacao = (g.empenhado || 0) - valorAnterior;
            const variacaoPct = valorAnterior > 0 ? (variacao / valorAnterior) * 100 : 0;
            const cor = variacao >= 0 ? '#28a745' : '#dc3545';
            html += `<tr><td>${g.nome}</td><td class="text-right">${fmt(g.empenhado)}</td><td class="text-right">${fmt(valorAnterior)}</td><td class="text-right" style="color: ${cor};">${fmt(variacao)}</td><td class="text-right" style="color: ${cor};">${fmt(variacaoPct)}%</td></tr>`;
        });
        
        const totalAnterior = gruposAn.reduce((acc, g) => acc + (g.empenhado || 0), 0);
        const varTotal = totalAtual - totalAnterior;
        const varTotalPct = totalAnterior > 0 ? (varTotal / totalAnterior) * 100 : 0;
        const corTotal = varTotal >= 0 ? '#28a745' : '#dc3545';
        
        html += `<tr class="total-row"><td>TOTAL</td><td class="text-right">${fmt(totalAtual)}</td><td class="text-right">${fmt(totalAnterior)}</td><td class="text-right" style="color: ${corTotal};">${fmt(varTotal)}</td><td class="text-right" style="color: ${corTotal};">${fmt(varTotalPct)}%</td></tr></tbody></table>`;
        
        document.getElementById('tabela-container').innerHTML = html;
    }''', c, flags=re.DOTALL)

open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] JavaScript blindado e refeito!")
