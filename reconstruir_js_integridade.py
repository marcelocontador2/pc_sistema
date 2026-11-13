import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_reconstrucao_integridade")

# Localiza o bloco <script>
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
        fetch(`/historico_integridade_matriz?_t=${Date.now()}`)
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

    // AQUI ESTÁ A CORREÇÃO: a função é async, mas o await é usado APENAS no fetch
    async function verificarMatriz() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('matriz-container');
        if (container) container.innerHTML = '<div class="loading">Buscando dados...</div>';

        try {
            // ÚNICO await do código: no fetch (que retorna Promise)
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            const data = await res.json(); // await no res.json() também é Promise

            if (data.erro) {
                alert("Aviso: " + data.mensagem);
                if (container) container.innerHTML = '';
                return;
            }

            dadosAtuais = data;

            if (container) {
                let html = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Descrição</th>
                                <th class="text-right">Valor (R$)</th>
                                <th>Consistente?</th>
                                <th>Observação</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                (data.matriz || []).forEach(m => {
                    const valor = m.valor_bp || m.valor_bo || m.valor_bf || m.valor_dvp || 0;
                    html += `
                        <tr>
                            <td>${m.descricao || ''}</td>
                            <td class="text-right">${formatarMoeda(valor)}</td>
                            <td>${m.consistente ? '✅' : '❌'}</td>
                            <td>${m.observacao || ''}</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            }
        } catch (err) {
            console.error(err);
            if (container) container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
        }
    }

    async function exibirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }

        try {
            const res = await fetch(`/historico_integridade_matriz/${id}`);
            const data = await res.json();

            if (data.erro) { alert("Erro: " + data.mensagem); return; }

            let payload = data.dados ? data.dados : data;
            if (typeof payload === 'string') {
                try { payload = JSON.parse(payload); } catch(e) {}
            }

            dadosAtuais = payload;

            const container = document.getElementById('matriz-container');
            if (container) {
                let html = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Descrição</th>
                                <th class="text-right">Valor (R$)</th>
                                <th>Consistente?</th>
                                <th>Observação</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                (payload.matriz || []).forEach(m => {
                    const valor = m.valor_bp || m.valor_bo || m.valor_bf || m.valor_dvp || 0;
                    html += `
                        <tr>
                            <td>${m.descricao || ''}</td>
                            <td class="text-right">${formatarMoeda(valor)}</td>
                            <td>${m.consistente ? '✅' : '❌'}</td>
                            <td>${m.observacao || ''}</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            }
        } catch (err) {
            alert("Erro ao carregar histórico: " + err);
        }
    }

    function gerarPDF() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        window.open(`/gerar_pdf_integridade/${id}`, '_blank');
    }

    function salvarAtual() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        fetch(`/api/integridade_matriz/${periodo}/salvar`, { method: 'POST' })
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

        fetch("/excluir_multiplos_integridade_matriz", {
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

print("✅ Bloco <script> da tela de Integridade reconstruído com sucesso!")
print("O await agora é usado APENAS no fetch (que retorna Promise).")
