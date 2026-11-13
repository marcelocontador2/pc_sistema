import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_recreate_final")

# 1. Remove qualquer botao Exibir antigo
s = re.sub(r'<button[^>]*onclick="exibirNovo\(\)"[^>]*>.*?</button>', '', s, flags=re.DOTALL)

# 2. Adiciona o botao Exibir ao lado do Gerar PDF
ancora = re.search(r'(<button[^>]*>\s*Gerar PDF\s*</button>)', s, re.IGNORECASE)
if ancora:
    novo_botao = ancora.group(1) + '\n        <button class="btn btn-salvar" onclick="exibirNovo()">Exibir</button>'
    s = s[:ancora.start()] + novo_botao + s[ancora.end():]
    print("OK: Botao 'Exibir' adicionado ao lado do 'Gerar PDF'.")

# 3. Adiciona a funcao exibirNovo se nao existir
if "function exibirNovo" not in s:
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
    }
}
"""
    s = s.replace('</script>', nova_func + '\n</script>')
    print("OK: Funcao exibirNovo() adicionada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
