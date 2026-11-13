import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_rota_def")

# 1. Remove TODAS as funcoes que possam estar sendo chamadas pelo botao Exibir
s = re.sub(r'async\s+function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', '', s, flags=re.DOTALL)
s = re.sub(r'async\s+function exibirNovo\(\)\s*\{.*?(?=\n\s*function|\Z)', '', s, flags=re.DOTALL)
s = re.sub(r'async\s+function exibirHistorico\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', '', s, flags=re.DOTALL)
print("OK: Funcoes antigas de exibicao removidas.")

# 2. Remove qualquer botao Exibir antigo
s = re.sub(r'<button[^>]*onclick="exibir[^"]*"[^>]*>.*?</button>', '', s, flags=re.DOTALL)
s = re.sub(r'<button[^>]*onclick="exibirNovo\(\)"[^>]*>.*?</button>', '', s, flags=re.DOTALL)
print("OK: Botoes antigos removidos.")

# 3. Adiciona o novo botao Exibir com ID unico
ancora = re.search(r'(<button[^>]*>\s*Gerar PDF\s*</button>)', s, re.IGNORECASE)
if ancora:
    novo_botao = ancora.group(1) + '\n        <button id="btn-exibir-final" class="btn btn-salvar">Exibir</button>'
    s = s[:ancora.start()] + novo_botao + s[ancora.end():]
    print("OK: Botao Exibir adicionado com ID 'btn-exibir-final'.")

# 4. Adiciona a nova funcao e o event listener no final do script
nova_func = """
async function exibirFinal() {
    const check = document.querySelector('.check-hist:checked') || document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    try {
        // A ROTA CORRETA DO POSTGRESQL (sem /id)
        const r = await fetch('/historico_composicao_receitas_despesas');
        if (!r.ok) throw new Error("HTTP " + r.status);
        const lista = await r.json();
        const item = lista.find(i => String(i.id) === String(idProcurado));
        if (!item) { alert("Histórico não encontrado."); return; }

        let dados = item.resultado_json;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = null; }
        }
        if (!dados) { alert("Dados vazios."); return; }

        const d = dados?.atual || dados || {};
        const dAnt = dados?.anterior || {};

        function fmtValor(v) {
            return (Number(v) || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

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
                html += `<tr><td>${key}</td><td style="text-align:right;">${fmtValor(val/1000)}</td><td style="text-align:right;">${fmtValor(vAnt/1000)}</td><td style="text-align:right;">${variacao}</td></tr>`;
            }
            tbRec.innerHTML = html;
        }

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
                html += `<tr><td>${key}</td><td style="text-align:right;">${fmtValor(val/1000)}</td><td style="text-align:right;">${fmtValor(vAnt/1000)}</td><td style="text-align:right;">${variacao}</td></tr>`;
            }
            tbDesp.innerHTML = html;
        }

        if (typeof renderChart === 'function') {
            renderChart(d, dAnt);
        }
    } catch (e) {
        alert("Erro ao carregar: " + e.message);
        console.error(e);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('btn-exibir-final');
    if (btn) {
        btn.addEventListener('click', exibirFinal);
        console.log("Event listener do botao Exibir Final configurado.");
    }
});
"""

s = s.replace('</script>', nova_func + '\n</script>')
print("OK: Funcao exibirFinal() e event listener adicionados.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
