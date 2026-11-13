import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_novo")

# 1. Remove o botao Exibir antigo (e qualquer onclick que chame exibirSelecionado)
s = re.sub(r'<button[^>]*onclick="exibirSelecionado\(\)"[^>]*>.*?</button>', '', s, flags=re.DOTALL)
s = re.sub(r'<button[^>]*onclick="exibirHistorico\([^)]*\)"[^>]*>.*?</button>', '', s, flags=re.DOTALL)

# 2. Remove a funcao exibirSelecionado antiga
s = re.sub(r'(async\s+)?function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', '', s, flags=re.DOTALL)
s = re.sub(r'(async\s+)?function exibirHistorico\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', '', s, flags=re.DOTALL)
print("OK: Botao e funcao antigos removidos.")

# 3. Adiciona o novo botao ao lado do "Verificar"
ancora = '<button class="btn btn-azul" onclick="carregar()">Verificar</button>'
novo_botao = ancora + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'

if ancora in s:
    s = s.replace(ancora, novo_botao, 1)
    print("OK: Novo botao 'Exibir' adicionado ao lado do 'Verificar'.")
else:
    print("AVISO: Ancora do botao 'Verificar' nao encontrada.")

# 4. Adiciona a nova funcao exibirNovo() no final do script (antes de </script>)
nova_func = """
async function exibirNovo() {
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
        if (!dados) { alert("Dados do histórico estão vazios."); return; }

        const d = dados?.atual || dados || {};
        const dAnt = dados?.anterior || {};

        // Preenche a tabela de Receitas
        const tbRec = document.querySelector('#tab-receitas tbody');
        if (tbRec) {
            let html = '';
            for (const [key, val] of Object.entries(d.receitas || {})) {
                const vAnt = (dAnt.receitas || {})[key] || 0;
                let variacao = '-';
                if (vAnt !== 0) {
                    const v = ((val - vAnt) / Math.abs(vAnt)) * 100;
                    variacao = (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
                }
                html += `<tr>
                    <td>${key}</td>
                    <td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td style="text-align:right;">${(vAnt/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td style="text-align:right;">${variacao}</td>
                </tr>`;
            }
            tbRec.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
        }

        // Preenche a tabela de Despesas
        const tbDesp = document.querySelector('#tab-despesas tbody');
        if (tbDesp) {
            let html = '';
            for (const [key, val] of Object.entries(d.despesas || {})) {
                const vAnt = (dAnt.despesas || {})[key] || 0;
                let variacao = '-';
                if (vAnt !== 0) {
                    const v = ((val - vAnt) / Math.abs(vAnt)) * 100;
                    variacao = (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
                }
                html += `<tr>
                    <td>${key}</td>
                    <td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td style="text-align:right;">${(vAnt/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td style="text-align:right;">${variacao}</td>
                </tr>`;
            }
            tbDesp.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
        }

        // Atualiza o grafico se a funcao existir
        if (typeof renderChart === 'function') {
            renderChart(d, dAnt);
        }
    } catch (e) {
        alert("Erro ao carregar o histórico: " + e.message);
        console.error(e);
    }
}
"""

if "function exibirNovo" not in s:
    s = s.replace('</script>', nova_func + '\n</script>')
    print("OK: Nova funcao exibirNovo() adicionada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
