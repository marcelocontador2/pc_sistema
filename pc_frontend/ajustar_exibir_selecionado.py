c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# Substitui a função exibirSelecionado por uma versão que busca os dados do período do histórico
antiga = """        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            const r = await fetch('/historico_comparativo_receitas/' + check.value);
            const d = await r.json();
            if (d.dados) { dadosAtuais = d.dados; renderizarTabela(d.dados); }
        }"""

nova = """        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            
            // Pega o período do histórico selecionado (ex: "2026-TRIMESTRE-3")
            const periodo = check.parentElement.querySelector('strong').innerText;
            
            try {
                // Busca os dados reais da API v2 para esse período
                const r = await fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                
                if (d.erro) {
                    document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">' + d.mensagem + '</div>';
                    return;
                }
                
                dadosAtuais = d;
                renderizarTabela(d);
                carregarResumo(); // Atualiza os cards
            } catch (e) {
                console.error(e);
                document.getElementById('tabela-container').innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Erro ao carregar dados.</div>';
            }
        }"""

if antiga in c:
    c = c.replace(antiga, nova)
    open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Função exibirSelecionado ajustada para carregar os dados do período do histórico!")
else:
    print("[AVISO] Função antiga não encontrada. Tentando regex...")
    import re
    padrao = r'async function exibirSelecionado\(\) \{.*?\n        \}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, nova, c, flags=re.DOTALL)
        open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
        print("[OK] Função substituída via regex!")
    else:
        print("[ERRO] Não foi possível encontrar a função exibirSelecionado.")
