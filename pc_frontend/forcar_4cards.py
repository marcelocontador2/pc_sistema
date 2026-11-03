import re

c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

# Novo grid de 4 cards
novo_grid = '''<div class="cards-grid" id="cards-resumo" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
        <div class="card">
            <div class="card-title">Despesa Orçada</div>
            <div class="card-value" id="resumo-orcado">R$ 0,00</div>
            <div class="card-sub" id="resumo-orcado-anterior">Anterior: R$ 0,00</div>
        </div>
        <div class="card">
            <div class="card-title">Despesa Empenhada</div>
            <div class="card-value" id="resumo-empenhado">R$ 0,00</div>
            <div class="card-sub" id="resumo-empenhado-anterior">Anterior: R$ 0,00</div>
        </div>
        <div class="card">
            <div class="card-title">Despesa Liquidada</div>
            <div class="card-value" id="resumo-liquidado">R$ 0,00</div>
            <div class="card-sub" id="resumo-liquidado-anterior">Anterior: R$ 0,00</div>
        </div>
        <div class="card">
            <div class="card-title">Execução Orçamentária</div>
            <div class="card-value" id="resumo-execucao">0,00%</div>
            <div class="card-sub" id="resumo-execucao-delta">—</div>
        </div>
    </div>'''

# Substitui o grid antigo (independente do conteúdo interno)
c = re.sub(r'<div class="cards-grid".*?</div>\s*</div>\s*</div>', novo_grid, c, flags=re.DOTALL)

# Atualiza a função atualizarCards
nova_func = '''function atualizarCards(d) {
            const at = d.atual;
            const an = d.anterior;
            const varExec = (at.percentual_total || 0) - (an.percentual_total || 0);
            
            document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total || 0);
            document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total || 0);
            
            document.getElementById('resumo-empenhado').innerText = 'R$ ' + fmt(at.empenhado_total || 0);
            document.getElementById('resumo-empenhado-anterior').innerText = 'Anterior: R$ ' + fmt(an.empenhado_total || 0);
            
            document.getElementById('resumo-liquidado').innerText = 'R$ ' + fmt(at.liquidado_total || 0);
            document.getElementById('resumo-liquidado-anterior').innerText = 'Anterior: R$ ' + fmt(an.liquidado_total || 0);
            
            document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total || 0) + '%';
            const deltaEl = document.getElementById('resumo-execucao-delta');
            deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
            deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
        }'''
c = re.sub(r'function atualizarCards\(d\) \{.*?\}', nova_func, c, flags=re.DOTALL)

open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado para 4 cards!")
