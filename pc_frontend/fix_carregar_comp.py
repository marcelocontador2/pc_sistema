import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Define a funcao carregar() baseada nos IDs reais (ano_atual, tipo_atual, val_atual)
nova_funcao_carregar = '''
function carregar() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    
    // Monta os periodos (Atual e Anterior)
    const pAtual = ano + '-' + tipo + '-' + val;
    const pAnterior = String(parseInt(ano) - 1) + '-' + tipo + '-' + val;
    
    // Limpa as tabelas antes de buscar
    document.querySelector('#tab-receitas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;">Buscando dados...</td></tr>';
    document.querySelector('#tab-despesas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;">Buscando dados...</td></tr>';
    
    // Faz a requisicao para os dois periodos em paralelo
    Promise.all([
        fetch('/api/composicao_receitas_despesas/' + pAtual).then(r => r.json()),
        fetch('/api/composicao_receitas_despesas/' + pAnterior).then(r => r.json())
    ]).then(([a, b]) => {
        if (a.erro) { alert('Período Atual: ' + a.mensagem); return; }
        if (b.erro) { alert('Período Anterior: ' + b.mensagem); return; }
        
        // Renderiza as tabelas
        renderTabela('tab-receitas', a.receitas, b.receitas);
        renderTabela('tab-despesas', a.despesas, b.despesas);
        
        // Renderiza o grafico
        renderChart(a, b);
    }).catch(e => {
        alert('Erro ao verificar dados: ' + e.message);
        console.error(e);
    });
}
'''

# Injeta a funcao carregar antes do DOMContentLoaded (ou antes do </script>)
if "function carregar()" not in s:
    # Encontra o inicio do script inline para inserir a funcao
    if "function fmtV(" in s:
        s = s.replace("function fmtV(", nova_funcao_carregar + "\nfunction fmtV(", 1)
    else:
        # Fallback: insere antes do </script>
        s = s.replace("</script>", nova_funcao_carregar + "\n</script>")
    print("OK: Funcao carregar() injetada com sucesso!")
else:
    print("OK: Funcao carregar() ja existe.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
