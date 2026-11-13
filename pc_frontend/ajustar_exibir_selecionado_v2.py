import re

c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# Substitui a função exibirSelecionado por uma versão que renderiza direto
antiga = r'async function exibirSelecionado\(\) \{.*?\n        \}'

nova = """        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            
            const periodo = check.parentElement.querySelector('strong').innerText;
            
            try {
                const r = await fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                
                if (d.erro) {
                    document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">' + d.mensagem + '</div>';
                    return;
                }
                
                dadosAtuais = d;
                renderizarTabela(d);
                
                // Atualiza os cards diretamente com os dados do período
                const at = d.atual;
                const an = d.anterior;
                const fmt = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                document.getElementById('resumo-realizado').innerText = 'R$ ' + fmt(at.realizado_total);
                document.getElementById('resumo-realizado-anterior').innerText = 'Anterior: R$ ' + fmt(an.realizado_total);
                document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total);
                document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total);
                document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total) + '%';
                const varExec = at.percentual_total - an.percentual_total;
                const deltaEl = document.getElementById('resumo-execucao-delta');
                deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
                deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
                
                // Atualiza também os filtros para o período do histórico
                const partes = periodo.split('-');
                if (partes.length === 3) {
                    document.getElementById('filtro-ano').value = partes[0];
                    document.getElementById('filtro-tipo').value = partes[1];
                    if (partes[1] === 'TRIMESTRE') {
                        document.getElementById('filtro-trimestre').value = partes[2];
                    }
                }
            } catch (e) {
                console.error(e);
                document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Erro ao carregar dados.</div>';
            }
        }"""

if re.search(antiga, c, re.DOTALL):
    c = re.sub(antiga, nova, c, flags=re.DOTALL)
    open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Função exibirSelecionado ajustada para renderizar direto!")
else:
    print("[ERRO] Função não encontrada.")
