import os
import re
import shutil

caminho_html = "pc_frontend/analise_comparativo_despesas.html"

if not os.path.exists(caminho_html):
    print("❌ HTML da tela de despesas não encontrado.")
    exit()

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho_html, caminho_html + ".bak_js_completo_despesas")

# 1. Garante que o botão "Verificar" tenha onclick correto
# Remove onclick antigo, se houver
html = re.sub(r'<button[^>]*class="[^"]*btn-verificar[^"]*"[^>]*>', '<button class="btn btn-verificar" onclick="verificar()">', html)

# 2. Remove qualquer bloco <script> antigo e insere um novo limpo
# Primeiro, localiza o bloco <script> existente
idx_inicio_script = html.find("<script>")
idx_fim_script = html.find("</script>", idx_inicio_script) + len("</script>")

if idx_inicio_script == -1:
    print("❌ Bloco <script> não encontrado. Inserindo um novo no final do <body>.")
    novo_script = '''
<script>
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
                // Se existir funções de renderização, chama
                if (typeof atualizarCards === 'function') atualizarCards(data);
                if (typeof renderizarTabela === 'function') renderizarTabela(data);
                else if (container) container.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
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
                const payload = data.dados ? data.dados : data;
                dadosAtuais = payload;
                if (typeof atualizarCards === 'function') atualizarCards(payload);
                if (typeof renderizarTabela === 'function') renderizarTabela(payload);
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
                if (data.erro) alert("Erro: " + data.mensagem);
                else { alert("Salvo com sucesso!"); window.location.reload(); }
            })
            .catch(err => alert("Erro ao salvar: " + err));
    }

    function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        if (!confirm("Tem certeza que deseja excluir?")) return;
        fetch("/excluir_multiplos_comparativo_despesas", {
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
</script>
'''
    html = html.replace("</body>", novo_script + "\n</body>")
else:
    # Se já existe um script, substitui por um novo
    novo_script = '''
<script>
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
                if (typeof atualizarCards === 'function') atualizarCards(data);
                if (typeof renderizarTabela === 'function') renderizarTabela(data);
                else if (container) container.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
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
                const payload = data.dados ? data.dados : data;
                dadosAtuais = payload;
                if (typeof atualizarCards === 'function') atualizarCards(payload);
                if (typeof renderizarTabela === 'function') renderizarTabela(payload);
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
                if (data.erro) alert("Erro: " + data.mensagem);
                else { alert("Salvo com sucesso!"); window.location.reload(); }
            })
            .catch(err => alert("Erro ao salvar: " + err));
    }

    function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        if (!confirm("Tem certeza que deseja excluir?")) return;
        fetch("/excluir_multiplos_comparativo_despesas", {
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
</script>
'''
    html = html[:idx_inicio_script] + novo_script + html[idx_fim_script:]

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML da tela de despesas reescrito com JavaScript completo!")
print("Agora aperte Ctrl+F5 na tela e teste.")
