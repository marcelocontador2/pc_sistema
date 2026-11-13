import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_render")

# Localiza a função renderizarTabela e substitui por uma versão "à prova de null"
nova_funcao = '''
function renderizarTabela(data) {
    const container = document.getElementById('tabela-container');
    if (!container) return;

    // Proteção contra data null
    if (!data) {
        container.innerHTML = '<div class="loading">Nenhum dado recebido.</div>';
        return;
    }

    const anteriorMap = {};
    // Verifica se data.anterior existe E se tem grupos
    if (data.anterior && Array.isArray(data.anterior.grupos)) {
        data.anterior.grupos.forEach(g => { anteriorMap[g.nome] = g; });
    }

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>GRUPO DE RECEITA</th>
                    <th class="text-right">PERÍODO ATUAL (R$)</th>
                    <th class="text-right">PERÍODO ANTERIOR (R$)</th>
                    <th class="text-right">VARIAÇÃO (R$)</th>
                    <th class="text-right">VARIAÇÃO (%)</th>
                </tr>
            </thead>
            <tbody>
    `;

    (data.grupos || []).forEach(g => {
        const atualVal = g.realizado || 0;
        const ant = anteriorMap[g.nome];
        const antVal = ant ? (ant.realizado || 0) : 0;
        const variacaoVal = atualVal - antVal;
        let variacaoPct = 0;
        if (antVal !== 0) variacaoPct = (variacaoVal / antVal) * 100;

        const classVar = variacaoVal < 0 ? 'val-negative' : (variacaoVal > 0 ? 'val-positive' : '');
        const sinal = variacaoVal > 0 ? '+' : '';

        html += `
            <tr>
                <td>${g.nome}</td>
                <td class="text-right">${formatarMoeda(atualVal)}</td>
                <td class="text-right">${formatarMoeda(antVal)}</td>
                <td class="text-right ${classVar}">${sinal}${formatarMoeda(variacaoVal)}</td>
                <td class="text-right ${classVar}">${sinal}${variacaoPct.toFixed(2)}%</td>
            </tr>
        `;
    });

    // Proteção contra data.realizado_total undefined
    const totalRealAtual = data.realizado_total || 0;
    const totalRealAnterior = (data.anterior && data.anterior.realizado_total) ? data.anterior.realizado_total : 0;
    const varTotal = totalRealAtual - totalRealAnterior;
    let varTotalPct = 0;
    if (totalRealAnterior !== 0) varTotalPct = (varTotal / totalRealAnterior) * 100;
    const classTotal = varTotal < 0 ? 'val-negative' : (varTotal > 0 ? 'val-positive' : '');
    const sinalTotal = varTotal > 0 ? '+' : '';

    html += `
            <tr class="total-row">
                <td><strong>TOTAL</strong></td>
                <td class="text-right"><strong>${formatarMoeda(totalRealAtual)}</strong></td>
                <td class="text-right"><strong>${formatarMoeda(totalRealAnterior)}</strong></td>
                <td class="text-right ${classTotal}"><strong>${sinalTotal}${formatarMoeda(varTotal)}</strong></td>
                <td class="text-right ${classTotal}"><strong>${sinalTotal}${varTotalPct.toFixed(2)}%</strong></td>
            </tr>
        </tbody>
    </table>
    `;

    container.innerHTML = html;
}
'''

# Localiza a função antiga e substitui
idx_inicio = html.find("function renderizarTabela")
if idx_inicio != -1:
    # Encontra o fim da função contando chaves
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_funcao.strip() + html[i:]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função renderizarTabela substituída por versão à prova de null!")
else:
    print("❌ Função renderizarTabela não encontrada.")
