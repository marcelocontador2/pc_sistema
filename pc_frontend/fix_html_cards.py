import re

c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

# Garante que a função JS está lendo os campos certos
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
print("[OK] Função atualizarCards do HTML atualizada!")
