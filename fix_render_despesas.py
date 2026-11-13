import re
import shutil

caminho = "pc_frontend/analise_comparativo_despesas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_render_despesas")

# Função renderizarTabela adaptada para despesas
nova_render = '''
function renderizarTabela(data) {
    const container = document.getElementById('tabela-container');
    if (!container) return;

    if (!data || data.erro) {
        container.innerHTML = '<div class="loading">Erro ao carregar dados.</div>';
        return;
    }

    const atual = data.atual || {};
    const anterior = data.anterior || {};

    // Mapeia os grupos do período anterior por nome
    const anteriorMap = {};
    if (anterior.grupos) {
        anterior.grupos.forEach(g => { anteriorMap[g.nome] = g; });
    }

    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>GRUPO DE DESPESA</th>
                    <th class="text-right">EMPENHADO ATUAL (R$)</th>
                    <th class="text-right">EMPENHADO ANTERIOR (R$)</th>
                    <th class="text-right">VARIAÇÃO (R$)</th>
                    <th class="text-right">VARIAÇÃO (%)</th>
                </tr>
            </thead>
            <tbody>
    `;

    (atual.grupos || []).forEach(g => {
        const atualVal = g.empenhado || 0;
        const ant = anteriorMap[g.nome];
        const antVal = ant ? (ant.empenhado || 0) : 0;
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

    const totalAtual = atual.empenhado_total || 0;
    const totalAnterior = anterior.empenhado_total || 0;
    const varTotal = totalAtual - totalAnterior;
    let varTotalPct = 0;
    if (totalAnterior !== 0) varTotalPct = (varTotal / totalAnterior) * 100;
    const classTotal = varTotal < 0 ? 'val-negative' : (varTotal > 0 ? 'val-positive' : '');
    const sinalTotal = varTotal > 0 ? '+' : '';

    html += `
            <tr class="total-row">
                <td><strong>TOTAL</strong></td>
                <td class="text-right"><strong>${formatarMoeda(totalAtual)}</strong></td>
                <td class="text-right"><strong>${formatarMoeda(totalAnterior)}</strong></td>
                <td class="text-right ${classTotal}"><strong>${sinalTotal}${formatarMoeda(varTotal)}</strong></td>
                <td class="text-right ${classTotal}"><strong>${sinalTotal}${varTotalPct.toFixed(2)}%</strong></td>
            </tr>
        </tbody>
    </table>
    `;

    container.innerHTML = html;
}
'''

# Procura a função renderizarTabela existente
idx_inicio = html.find("function renderizarTabela")
if idx_inicio != -1:
    # Conta chaves para achar o fim
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_render.strip() + html[i:]
    print("✅ Função renderizarTabela substituída.")
else:
    # Se não existe, insere antes de </script>
    html = html.replace("</script>", nova_render + "\n</script>")
    print("✅ Função renderizarTabela criada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

# Verifica se a função verificar() chama renderizarTabela e atualizarCards
if "atualizarCards" not in html or "typeof atualizarCards" in html:
    # Cria uma atualizarCards simples se não existir
    nova_cards = '''
function atualizarCards(data) {
    const atual = data.atual || {};
    const anterior = data.anterior || {};
    
    const cardEmpenhado = document.getElementById('card-realizado') || document.getElementById('card-empenhado');
    if (cardEmpenhado) cardEmpenhado.innerText = formatarMoeda(atual.empenhado_total);
    
    const cardOrcado = document.getElementById('card-orcado');
    if (cardOrcado) cardOrcado.innerText = formatarMoeda(atual.orcado_total);
    
    const cardPercentual = document.getElementById('card-percentual');
    if (cardPercentual) cardPercentual.innerText = (atual.percentual_total || 0).toFixed(2) + '%';
}
'''
    if "function atualizarCards" in html:
        idx = html.find("function atualizarCards")
        i = html.find("{", idx)
        contador = 1
        i += 1
        while i < len(html) and contador > 0:
            if html[i] == "{": contador += 1
            elif html[i] == "}": contador -= 1
            i += 1
        html = html[:idx] + nova_cards.strip() + html[i:]
    else:
        html = html.replace("</script>", nova_cards + "\n</script>")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função atualizarCards ajustada.")

print("✅ Arquivo salvo.")
