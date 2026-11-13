import shutil

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_html_limpo")

novo_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Consolidado - Análise Contábil</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; color: #333; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #003366; font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #004b8d; padding-bottom: 10px; }
        .barra-botoes { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        button { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; color: #fff; font-size: 14px; }
        .btn-verde { background-color: #198754; }
        .btn-vermelho { background-color: #dc3545; }
        .btn-azul { background-color: #0d6efd; }
        .btn-verde:hover { background-color: #157347; }
        .btn-vermelho:hover { background-color: #bb2d3b; }
        .btn-azul:hover { background-color: #0b5ed7; }
        .filtros { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; align-items: center; background: #f8f9fa; padding: 15px; border-radius: 6px; }
        .filtros label { font-weight: bold; color: #555; }
        .filtros select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .alerta { padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .alerta-amarelo { background-color: #fff3cd; border: 1px solid #ffecb5; color: #664d03; }
        .alerta-verde { background-color: #d1e7dd; border: 1px solid #badbcc; color: #0f5132; }
        .status-modulos { margin-top: 20px; }
        .modulo-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; align-items: center; }
        .modulo-item:last-child { border-bottom: none; }
        .modulo-nome { font-size: 14px; }
        .modulo-ok { color: #198754; font-weight: bold; }
        .modulo-faltando { color: #dc3545; font-weight: bold; }
        .secao { margin-top: 30px; }
        .secao h2 { font-size: 18px; color: #003366; margin-bottom: 15px; }
        .historico-lista { list-style: none; }
        .historico-lista li { padding: 8px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px; font-size: 13px; }
        .historico-lista li:last-child { border-bottom: none; }
        .historico-lista input[type="checkbox"] { margin-right: 5px; }
        .historico-lista .data { color: #666; font-size: 12px; }
        .loading { text-align: center; padding: 20px; color: #666; font-style: italic; }
        .erro { color: red; padding: 20px; background: #ffe6e6; border: 1px solid red; border-radius: 6px; }
        .flex-row { display: flex; gap: 20px; }
        .flex-col { flex: 1; }
        @media (max-width: 768px) { .flex-row { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Relatório Consolidado de Análise Contábil</h1>

        <div class="barra-botoes">
            <button class="btn-azul" onclick="window.history.back()">← Voltar</button>
            <button class="btn-verde" onclick="exibirSelecionado()">Exibir Selecionado</button>
            <button class="btn-vermelho" onclick="excluirSelecionado()">Excluir Selecionado</button>
            <button class="btn-azul" onclick="gerarPDF()">Gerar PDF</button>
            <button class="btn-verde" onclick="salvarRelatorioConsolidado()" style="margin-left: auto;">Confirmar e Salvar</button>
            <button class="btn-azul" onclick="abrirObservacoes()">Observações</button>
            <button class="btn-azul" onclick="abrirConclusao()">Conclusão</button>
        </div>

        <div class="filtros">
            <label>Ano:</label>
            <select id="ano">
                <option value="2026" selected>2026</option>
                <option value="2025">2025</option>
            </select>
            <label>Tipo:</label>
            <select id="tipo_periodo">
                <option value="TRIMESTRE" selected>Trimestral</option>
                <option value="SEMESTRE">Semestral</option>
                <option value="ANO">Anual</option>
            </select>
            <label>Período:</label>
            <select id="trimestre">
                <option value="1">1º</option>
                <option value="2">2º</option>
                <option value="3" selected>3º</option>
                <option value="4">4º</option>
            </select>
            <button class="btn-verde" onclick="verificarDados()">Verificar Dados</button>
        </div>

        <div id="mensagem-consolidado"></div>
        <div id="status-modulos" class="status-modulos"></div>
    </div>

    <script>
        // ============================================================
        // ESTADO GLOBAL
        // ============================================================
        let dadosAtuais = null;
        let relatorioIdSelecionado = null;

        // ============================================================
        // FUNÇÕES DE FORMATAÇÃO
        // ============================================================
        function formatarMoeda(valor) {
            if (valor === null || valor === undefined || valor === '-' || valor === '') return '-';
            if (typeof valor === 'string' && valor.includes('R$')) return valor;
            return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }

        // ============================================================
        // VERIFICAR DADOS (API)
        // ============================================================
        async function verificarDados() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo_periodo').value;
            const trimestre = document.getElementById('trimestre').value;
            const periodo = ano + '-' + tipo + '-' + trimestre;

            const divMsg = document.getElementById('mensagem-consolidado');
            const divStatus = document.getElementById('status-modulos');
            
            divMsg.innerHTML = '<div class="loading">Buscando dados no PostgreSQL...</div>';
            divStatus.innerHTML = '';

            try {
                const res = await fetch('/api/relatorio_consolidado/' + periodo + '?_t=' + Date.now());
                const data = await res.json();

                if (data.status === 'erro') {
                    divMsg.innerHTML = '<div class="erro">Erro: ' + (data.mensagem || 'Erro desconhecido') + '</div>';
                    return;
                }

                dadosAtuais = data;

                if (data.faltando && data.faltando.length > 0) {
                    divMsg.innerHTML = '<div class="alerta alerta-amarelo"><strong>⚠ Faltam ' + data.faltando.length + ' módulo(s) para consolidar.</strong><br>Realize os cálculos dos módulos pendentes antes de gerar o relatório.</div>';
                } else {
                    divMsg.innerHTML = '<div class="alerta alerta-verde"><strong>✅ Todos os módulos estão prontos para consolidar!</strong></div>';
                }

                let html = '<h2>Status dos Módulos:</h2>';
                
                if (data.encontrados && data.encontrados.length > 0) {
                    html += '<h3 style="color: #198754; margin: 15px 0 10px;">✓ Encontrados:</h3>';
                    data.encontrados.forEach(function(m, i) {
                        html += '<div class="modulo-item"><span class="modulo-nome">' + (i+1) + '. ' + m.nome + '</span><span class="modulo-ok">✓ ' + (m.data_geracao || 'Disponível') + '</span></div>';
                    });
                }

                if (data.faltando && data.faltando.length > 0) {
                    html += '<h3 style="color: #dc3545; margin: 15px 0 10px;">✗ Faltando:</h3>';
                    data.faltando.forEach(function(m, i) {
                        html += '<div class="modulo-item"><span class="modulo-nome">' + (i+1) + '. ' + m.nome + '</span><span class="modulo-faltando">✗ Faltando</span></div>';
                    });
                }

                divStatus.innerHTML = html;

            } catch (err) {
                console.error(err);
                divMsg.innerHTML = '<div class="erro">Erro de conexão: ' + err.message + '</div>';
            }
        }

        // ============================================================
        // SALVAR RELATÓRIO CONSOLIDADO
        // ============================================================
        async function salvarRelatorioConsolidado() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo_periodo').value;
            const trimestre = document.getElementById('trimestre').value;
            const periodo = ano + '-' + tipo + '-' + trimestre;

            if (!confirm("Deseja realmente salvar este relatório consolidado no histórico?")) return;

            try {
                console.log("Chamando rota /salvar_relatorio_consolidado/" + periodo);
                
                const res = await fetch('/salvar_relatorio_consolidado/' + periodo, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (!res.ok) {
                    const texto = await res.text();
                    throw new Error('HTTP ' + res.status + ': ' + texto.substring(0, 200));
                }
                
                const data = await res.json();
                console.log("Resposta do backend:", data);
                
                if (data.ok) {
                    alert("Relatório salvo com sucesso no PostgreSQL!");
                    if (typeof carregarHistorico === 'function') {
                        carregarHistorico();
                    }
                } else {
                    alert("Erro ao salvar: " + (data.mensagem || "Erro desconhecido"));
                }
            } catch (err) {
                console.error("Erro completo:", err);
                alert("Erro de conexão ao salvar: " + err.message);
            }
        }

        // ============================================================
        // HISTÓRICO (LISTA LATERAL)
        // ============================================================
        async function carregarHistorico() {
            try {
                const res = await fetch('/historico_relatorio_consolidado?_t=' + Date.now());
                const data = await res.json();
                
                const lista = document.getElementById('historico-lista');
                if (!lista) return;
                
                if (Array.isArray(data) && data.length > 0) {
                    lista.innerHTML = data.map(function(h) {
                        return '<li><input type="checkbox" value="' + h.id + '"><span>ID: ' + h.id + ' | Período: ' + h.periodo + ' | Data: ' + h.data_geracao + '</span></li>';
                    }).join('');
                } else {
                    lista.innerHTML = '<li>Nenhum histórico salvo.</li>';
                }
            } catch (err) {
                console.error('Erro ao carregar histórico:', err);
            }
        }

        // ============================================================
        // EXIBIR / EXCLUIR / PDF (PLACEHOLDERS)
        // ============================================================
        function exibirSelecionado() {
            const checkbox = document.querySelector('#historico-lista input[type="checkbox"]:checked');
            if (!checkbox) { alert("Selecione um histórico na lista."); return; }
            const id = checkbox.value;
            fetch('/historico_relatorio_consolidado/' + id)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.erro) { alert("Erro: " + data.mensagem); return; }
                    alert("Relatório ID " + id + " carregado. (Implementar renderização)");
                })
                .catch(function(err) { alert("Erro: " + err.message); });
        }

        function excluirSelecionado() {
            const checkbox = document.querySelector('#historico-lista input[type="checkbox"]:checked');
            if (!checkbox) { alert("Selecione um histórico na lista."); return; }
            if (!confirm("Excluir o histórico selecionado?")) return;
            const id = checkbox.value;
            fetch('/excluir_relatorio_consolidado/' + id, { method: 'DELETE' })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.ok) {
                        carregarHistorico();
                    } else {
                        alert("Erro: " + (data.mensagem || "Erro desconhecido"));
                    }
                })
                .catch(function(err) { alert("Erro: " + err.message); });
        }

        function gerarPDF() {
            const checkbox = document.querySelector('#historico-lista input[type="checkbox"]:checked');
            if (!checkbox) { alert("Selecione um histórico na lista."); return; }
            window.open('/gerar_pdf_relatorio_consolidado/' + checkbox.value, '_blank');
        }

        function abrirObservacoes() { alert("Funcionalidade de Observações em desenvolvimento."); }
        function abrirConclusao() { alert("Funcionalidade de Conclusão em desenvolvimento."); }

        // ============================================================
        // INICIALIZAÇÃO
        // ============================================================
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Página carregada. Botão de salvar disponível:', typeof salvarRelatorioConsolidado);
        });
    </script>
</body>
</html>"""

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(novo_html)

print("✅ relatorio_consolidado.html reescrito do zero com botão funcional!")
