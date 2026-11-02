c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# A função antiga (pega só 1)
funcao_antiga = """        function excluirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            if (confirm('Tem certeza que deseja excluir este relatório?')) {
                fetch('/excluir_custo_pessoal/' + check.value, { method: 'DELETE' })
                    .then(() => carregarHistorico());
            }
        }"""

# A função nova (pega todos os marcados)
funcao_nova = """        function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert('Selecione pelo menos um item no histórico.'); return; }
            
            if (confirm('Tem certeza que deseja excluir ' + checks.length + ' relatório(s)?')) {
                // Monta a lista de IDs
                const ids = Array.from(checks).map(c => parseInt(c.value));
                
                // Envia para o backend
                fetch('/excluir_multiplos_custo_pessoal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: ids })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.ok) {
                        alert('Excluídos ' + res.excluidos + ' relatório(s).');
                        carregarHistorico();
                    } else {
                        alert('Erro ao excluir.');
                    }
                })
                .catch(e => {
                    console.error(e);
                    alert('Erro ao excluir.');
                });
            }
        }"""

if funcao_antiga in c:
    c = c.replace(funcao_antiga, funcao_nova)
    print("[OK] JavaScript da exclusão múltipla corrigido!")
else:
    print("[AVISO] Não foi possível encontrar a função exata. Tentando abordagem alternativa...")
    import re
    c = re.sub(r'function excluirSelecionado\(\) \{.*?\n        \}', funcao_nova, c, flags=re.DOTALL)
    print("[OK] Função substituída via regex!")

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
