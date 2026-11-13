import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_exibir_correto")

# Funcao que sera usada em ambos os casos
nova_func = """async function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked') || document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    try {
        const r = await fetch('/historico_composicao_receitas_despesas');
        if (!r.ok) throw new Error("HTTP " + r.status);
        const lista = await r.json();
        const item = lista.find(i => String(i.id) === String(idProcurado));
        if (!item) { alert("Histórico não encontrado."); return; }

        let dados = item.resultado_json;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = null; }
        }
        
        const d = dados?.atual || dados || {};

        // Preenche a tabela de Receitas
        const tbRec = document.getElementById('tbody-receitas');
        if (tbRec) {
            let html = '';
            for (const [key, val] of Object.entries(d.receitas || {})) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbRec.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
        }

        // Preenche a tabela de Despesas
        const tbDesp = document.getElementById('tbody-despesas');
        if (tbDesp) {
            let html = '';
            for (const [key, val] of Object.entries(d.despesas || {})) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbDesp.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
        }

        // Atualiza o grafico
        if (typeof renderChart === 'function') {
            renderChart(d);
        }
    } catch (e) {
        alert("Erro ao carregar o histórico: " + e.message);
        console.error(e);
    }
}
"""

# Tenta substituir a funcao existente (exibirSelecionado ou exibirHistorico)
padrao1 = re.compile(r'(async\s+)?function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match1 = padrao1.search(s)

if match1:
    s = s[:match1.start()] + nova_func + s[match1.end():]
    print("OK: Funcao exibirSelecionado() substituida.")
else:
    padrao2 = re.compile(r'(async\s+)?function exibirHistorico\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
    match2 = padrao2.search(s)
    if match2:
        s = s[:match2.start()] + nova_func + s[match2.end():]
        print("OK: Funcao exibirHistorico() substituida.")
    else:
        # Se nao achar, insere a nova funcao antes do fechamento do script
        s = s.replace('</script>', nova_func + '\n</script>')
        print("OK: Nova funcao exibirSelecionado() inserida.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
