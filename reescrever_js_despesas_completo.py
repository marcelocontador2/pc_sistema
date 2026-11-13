import re
import shutil

caminho = "pc_frontend/analise_comparativo_despesas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_reconstrucao_js_despesas")

# Localiza o bloco <script> para substituir
idx_inicio = html.find("<script>")
idx_fim = html.find("</script>", idx_inicio) + len("</script>")

novo_script = '''<script>
    let dadosAtuais = null;

    function formatarMoeda(valor) {
        return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function getHistoricoSelecionado() {
        const checkboxes = document.querySelectorAll('#historico-lista input[type="checkbox"]');
        for (let cb of checkboxes) {
            if (cb.checked) return cb.value;
        }
        return null;
    }

    document.addEventListener("DOMContentLoaded", () => {
        carregarHistorico();
    });

    function carregarHistorico() {
        const list = document.getElementById('historico-lista');
        if (!list) return;
        list.innerHTML = '<li class="loading">Carregando histórico...</li>';
        fetch(`/historico_comparativo_despesas?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                list.innerHTML = '';
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(h => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <input type="checkbox" value="${h.id}">
                            <span>Período: ${h.periodo} | Gerado em: ${h.data_geracao || h.criado_em || 'N/A'}</span>
                        `;
                        list.appendChild(li);
                    });
                } else {
                    list.innerHTML = '<li>Nenhum histórico salvo.</li>';
                }
            })
            .catch(err => {
                list.innerHTML = '<li>Erro ao carregar histórico.</li>';
                console.error(err);
            });
    }

    function atualizarCards(data) {
        const atual = (data && data.atual) ? data.atual : (data || {});
        const anterior = (data && data.anterior) ? data.anterior : {};

        const cardEmp = document.getElementById('card-realizado') || document.getElementById('card-empenhado');
        if (cardEmp) cardEmp.innerText = formatarMoeda(atual.empenhado_total);

        const cardOrc = document.getElementById('card-orcado');
        if (cardOrc) cardOrc.innerText = formatarMoeda(atual.orcado_total);

        const cardPct = document.getElementById('card-percentual');
        if (cardPct) cardPct.innerText = (atual.percentual_total || 0).toFixed(2) + '%';

        // Subtextos "Anterior:"
        const subEmp = document.getElementById('sub-realizado');
        if (subEmp) subEmp.innerText = `Anterior: ${formatarMoeda(anterior.empenhado_total)}`;
        
        const subOrc = document.getElementById('sub-orcado');
        if (subOrc) subOrc.innerText = `Anterior: ${formatarMoeda(anterior.orcado_total)}`;
    }

    function renderizarTabela(data) {
        const container = document.getElementById('tabela-container');
        if (!container) return;

        const atual = (data && data.atual) ? data.atual : (data || {});
        const anterior = (data && data.anterior) ? data.anterior : {};

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

    function verificar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const valor = document.getElementById('valor').value;
        const periodo = `${ano}-${tipo}-${valor}`;

        const container = document.getElementById('tabela-container');
        if (container) container.innerHTML = '<div class="loading">Buscando dados...</div>';

        fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    alert("Aviso: " + data.mensagem);
                    if (container) container.innerHTML = '';
                    return;
                }
                dadosAtuais = data;
                atualizarCards(data);
                renderizarTabela(data);
            })
            .catch(err => {
                console.error(err);
                if (container) container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
            });
    }

    function exibirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }

        fetch(`/historico_comparativo_despesas/${id}`)
            .then(res => res.json())
            .then(data => {
                if (data.erro) { alert("Erro: " + data.mensagem); return; }
                
                let payload = data.dados ? data.dados : data;
                if (typeof payload === 'string') {
                    try { payload = JSON.parse(payload); } catch(e) {}
                }
                
                // Se o payload já tem "atual", usa; senão envelopa
                if (payload && payload.atual) {
                    dadosAtuais = payload;
                } else {
                    dadosAtuais = { atual: payload, anterior: null };
                }
                
                atualizarCards(dadosAtuais);
                renderizarTabela(dadosAtuais);
            })
            .catch(err => alert("Erro ao carregar histórico: " + err));
    }

    function gerarPDF() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        window.open(`/gerar_pdf_comparativo_despesas/${id}`, '_blank');
    }

    function salvarAtual() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const valor = document.getElementById('valor').value;
        const periodo = `${ano}-${tipo}-${valor}`;
        
        fetch(`/api/comparativo_despesas_v2/${periodo}/salvar`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    alert("Erro: " + data.mensagem);
                } else {
                    alert("Salvo com sucesso!");
                    window.location.reload();
                }
            })
            .catch(err => alert("Erro ao salvar: " + err));
    }

    function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        if (!confirm("Tem certeza que deseja excluir o histórico selecionado?")) return;

        fetch("/excluir_multiplos_comparativo_despesas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: [id] })
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                carregarHistorico();
            } else {
                alert("Erro ao excluir: " + (data.mensagem || "Erro desconhecido"));
            }
        })
        .catch(err => alert("Erro ao excluir: " + err));
    }
</script>'''

html = html[:idx_inicio] + novo_script + html[idx_fim:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Bloco <script> da tela de Despesas completamente reescrito!")
