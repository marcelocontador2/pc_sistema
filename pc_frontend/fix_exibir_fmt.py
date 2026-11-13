import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_exibir_fmt")

# Encontra a funcao exibirNovo()
padrao = re.compile(r'async\s+function exibirNovo\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """async function exibirNovo() {
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

        // Formata valor no padrao brasileiro (sem cortar zeros)
        function fmtValor(v) {
            const n = Number(v) || 0;
            return n.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

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
                    <td style="text-align:right;">${fmtValor(val/1000)}</td>
                    <td style="text-align:right;">${fmtValor(vAnt/1000)}</td>
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
                    <td style="text-align:right;">${fmtValor(val/1000)}</td>
                    <td style="text-align:right;">${fmtValor(vAnt/1000)}</td>
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
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao exibirNovo() corrigida com formatacao brasileira.")
else:
    print("ERRO: Funcao exibirNovo() nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
