import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao carregar() inteira por uma versao com mensagens amigaveis
padrao = re.compile(r'function\s+carregar\(\)\s*\{.*?\n\}', re.DOTALL)

nova_carregar = '''function carregar() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    
    const pAtual = ano + '-' + tipo + '-' + val;
    const pAnterior = String(parseInt(ano) - 1) + '-' + tipo + '-' + val;
    
    // Limpa as tabelas
    document.querySelector('#tab-receitas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;">Buscando dados...</td></tr>';
    document.querySelector('#tab-despesas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;">Buscando dados...</td></tr>';
    
    Promise.all([
        fetch('/api/composicao_receitas_despesas/' + pAtual).then(r => r.json()),
        fetch('/api/composicao_receitas_despesas/' + pAnterior).then(r => r.json())
    ]).then(([a, b]) => {
        // Verifica se o backend retornou erro ou lista vazia
        if (a.erro || !a.receitas || Object.keys(a.receitas).length === 0) {
            alert("Aviso: Não há dados importados para o período atual (" + pAtual + "). Verifique se os relatórios foram importados.");
            document.querySelector('#tab-receitas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center; color:#856404;">Nenhum dado para o período.</td></tr>';
            document.querySelector('#tab-despesas tbody').innerHTML = '<tr><td colspan="4" style="text-align:center; color:#856404;">Nenhum dado para o período.</td></tr>';
            return;
        }
        if (b.erro || !b.receitas || Object.keys(b.receitas).length === 0) {
            alert("Aviso: Não há dados importados para o período anterior (" + pAnterior + "). Verifique se os relatórios foram importados.");
            return;
        }
        
        renderTabela('tab-receitas', a.receitas, b.receitas);
        renderTabela('tab-despesas', a.despesas, b.despesas);
        renderChart(a, b);
    }).catch(e => {
        alert("Erro ao verificar dados: " + e.message);
        console.error(e);
    });
}'''

nova_s, n = padrao.subn(nova_carregar, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao carregar() atualizada com mensagens de erro amigaveis!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao carregar().")
