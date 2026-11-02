c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# Substitui a função excluirSelecionado para pegar todos os checkboxes marcados
funcao_antiga = '''        async function excluirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            if (!confirm('Deseja excluir este item?')) return;
            const r = await fetch('/historico_centro_custos/' + check.value, { method: 'DELETE' });
            const res = await r.json();
            if (res.ok) { alert('Excluído!'); carregarHistorico(); }
            else { alert('Erro ao excluir.'); }
        }'''

funcao_nova = '''        async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert('Selecione pelo menos um item no histórico.'); return; }
            
            if (!confirm('Tem certeza que deseja excluir ' + checks.length + ' relatório(s)?')) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {
                const r = await fetch('/excluir_multiplos_centro_custos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: ids })
                });
                const res = await r.json();
                if (res.ok) {
                    alert('Excluídos ' + res.excluidos + ' relatório(s).');
                    carregarHistorico();
                } else {
                    alert('Erro ao excluir.');
                }
            } catch (e) {
                console.error(e);
                alert('Erro ao excluir.');
            }
        }'''

if funcao_antiga in c:
    c = c.replace(funcao_antiga, funcao_nova)
    print("[OK] Função de exclusão múltipla corrigida!")
else:
    print("[AVISO] Função antiga não encontrada. Tentando regex...")
    import re
    c = re.sub(r'async function excluirSelecionado\(\) \{.*?\n        \}', funcao_nova, c, flags=re.DOTALL)
    print("[OK] Função substituída via regex!")

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Tela atualizada!")
