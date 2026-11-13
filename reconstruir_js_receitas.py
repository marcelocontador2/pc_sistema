import re
import shutil

path = "pc_frontend/analise_comparativo_receitas.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(path, path + ".bak_reconstrucao_js")

# 1. Localiza o início e o fim do bloco <script> para substituir tudo de uma vez
idx_inicio = html.find("<script>")
idx_fim = html.find("</script>", idx_inicio)

if idx_inicio == -1 or idx_fim == -1:
    print("❌ Bloco <script> não encontrado no arquivo.")
    exit()

# Nossa nova lógica JavaScript completa e testada
novo_script = '''<script>
    let dadosAtuais = null;

    function formatarMoeda(valor) {
        return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function getHistoricoSelecionado() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        for (let cb of checkboxes) {
            if (cb.checked && cb.value) return cb.value;
        }
        return null;
    }

    // Inicialização da tela
    document.addEventListener("DOMContentLoaded", () => {
        carregarHistorico();
    });

    function carregarHistorico() {
        fetch(`/historico_comparativo_receitas?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                const list = document.getElementById('historico-lista');
                if (!list) return;
                list.innerHTML = '';
                if (data && data.length > 0) {
                    data.forEach(h => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <input type="checkbox" value="${h.id}" onchange="atualizarSelecao()">
                            <span>Período: ${h.periodo} | Gerado em: ${h.data_geracao || h.criado_em}</span>
                        `;
                        list.appendChild(li);
                    });
                } else {
                    list.innerHTML = '<li>Nenhum histórico salvo.</li>';
                }
            })
            .catch(err => console.error("Erro ao carregar histórico:", err));
    }

    function verificar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const valor = document.getElementById('valor').value;
        const periodo = `${ano}-${tipo}-${valor}`;

        const container = document.getElementById('tabela-container');
        container.innerHTML = '<div class="loading">Buscando dados...</div>';

        fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    alert("Aviso: " + data.mensagem);
                    container.innerHTML = '';
                    return;
                }
                dadosAtuais = data;
                atualizarCards(data);
                renderizarTabela(data);
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
            });
    }

    function atualizarCards(data) {
        if (document.getElementById('card-realizado'))
            document.getElementById('card-realizado').innerText = formatarMoeda(data.realizado_total);
        
        if (document.getElementById('card-orcado'))
            document.getElementById('card-orcado').innerText = formatarMoeda(data.orcado_total);
        
        if (document.getElementById('card-percentual'))
            document.getElementById('card-percentual').innerText = (data.percentual_total || 0).toFixed(2) + '%';

        // Preenche os subtextos "Anterior:"
        if (data.anterior) {
            const subReal = document.getElementById('sub-realizado');
            if (subReal) subReal.innerText = `Anterior: ${formatarMoeda(data.anterior.realizado_total)}`;
            
            const subOrc = document.getElementById('sub-orcado');
            if (subOrc) subOrc.innerText = `Anterior: ${formatarMoeda(data.anterior.orcado_total)}`;
            
            const subPct = document.getElementById('sub-percentual');
            if (subPct) {
                let diff = (data.percentual_total || 0) - (data.anterior.percentual_total || 0);
                subPct.innerText = `${diff > 0 ? '+' : ''}${diff.toFixed(2)} p.p.`;
            }
        }
    }

    function renderizarTabela(data) {
        const container = document.getElementById('tabela-container');
        if (!container) return;

        const anteriorMap = {};
        if (data.anterior && data.anterior.grupos) {
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

    function exibirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        
        fetch(`/historico_comparativo_receitas/${id}`)
            .then(res => res.json())
            .then(data => {
                if (data.erro) { alert("Erro: " + data.mensagem); return; }
                if (data.dados) {
                    dadosAtuais = data.dados;
                    atualizarCards(dadosAtuais);
                    renderizarTabela(dadosAtuais);
                } else {
                    // Se a API retornar o próprio objeto no nível raiz
                    dadosAtuais = data;
                    atualizarCards(dadosAtuais);
                    renderizarTabela(dadosAtuais);
                }
            })
            .catch(err => alert("Erro ao carregar histórico: " + err));
    }

    function gerarPDF() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        window.open(`/gerar_pdf_comparativo_receitas/${id}`, '_blank');
    }

    function salvarAtual() {
        if (!dadosAtuais) { alert("Verifique os dados primeiro."); return; }
        // Pega o período atual da tela
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const valor = document.getElementById('valor').value;
        const periodo = `${ano}-${tipo}-${valor}`;

        fetch(`/api/comparativo_receitas_v2/${periodo}/salvar`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.erro) alert("Erro: " + data.mensagem);
                else { alert("Salvo com sucesso!"); carregarHistorico(); }
            })
            .catch(err => alert("Erro ao salvar: " + err));
    }

    function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        
        if (!confirm("Tem certeza que deseja excluir o histórico selecionado?")) return;

        fetch("/excluir_multiplos_comparativo_receitas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: [id] })
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) { carregarHistorico(); }
            else { alert("Erro ao excluir."); }
        })
        .catch(err => alert("Erro ao excluir: " + err));
    }
</script>'''

html = html[:idx_inicio] + novo_script + html[idx_fim + len("</script>"):]

# 2. Garantir que os IDs nos cards e na tabela existam no HTML
# Adiciona IDs nos elementos de subtexto, caso não existam
if 'id="sub-realizado"' not in html:
    html = html.replace("Anterior: R$ 181.491.878,72", '<span id="sub-realizado">Anterior: R$ 181.491.878,72</span>')
if 'id="sub-orcado"' not in html:
    html = html.replace("Anterior: R$ 229.685.000,00", '<span id="sub-orcado">Anterior: R$ 229.685.000,00</span>')
if 'id="sub-percentual"' not in html:
    html = html.replace("+0,56 p.p.", '<span id="sub-percentual">+0,56 p.p.</span>')

# 3. Garantir que os botões chamem as funções corretas e os cards tenham IDs
html = html.replace('<button class="btn btn-verificar" onclick="verificarDados()">', '<button class="btn btn-verificar" onclick="verificar()">')
html = html.replace('id="receita-realizada"', 'id="card-realizado"')
html = html.replace('id="receita-orcada"', 'id="card-orcado"')
html = html.replace('id="execucao-orcamentaria"', 'id="card-percentual"')

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ O bloco <script> inteiro foi reconstruído com funções limpas!")
print("Agora aperte Ctrl+F5 na tela e tudo deve funcionar.")
