
    // 1. CARREGA A LISTA DE HISTORICO
    function carregarHistorico() {
        var lista = document.getElementById('lista-historico');
        if (!lista) return;
        lista.innerHTML = '<li>Carregando...</li>';
        
        fetch('/historico_relatorio_consolidado')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data && data.length > 0) {
                    var html = '';
                    for (var i = 0; i < data.length; i++) {
                        var h = data[i];
                        html += '<li style="display:flex; align-items:center; gap:8px; padding:8px 0; border-bottom:1px solid #eee;">';
                        html += '<input type="checkbox" class="chk-historico" value="' + h.id + '" onchange="atualizarBotao()">';
                        html += '<span>Período: ' + h.periodo + '<br><small style="color:#999;">' + (h.data_geracao || 'N/A') + '</small></span>';
                        html += '</li>';
                    }
                    lista.innerHTML = html;
                } else {
                    lista.innerHTML = '<li style="color:#666;">Nenhum histórico salvo.</li>';
                }
                atualizarBotao();
            })
            .catch(function(e) {
                lista.innerHTML = '<li style="color:red;">Erro: ' + e + '</li>';
            });
    }

    // 2. ATUALIZA O BOTAO DE EXCLUIR
    function atualizarBotao() {
        var btn = document.getElementById('btn-excluir-todos');
        if (!btn) return;
        var checkboxes = document.querySelectorAll('.chk-historico:checked');
        btn.disabled = (checkboxes.length === 0);
    }

    // 3. MARCA TODOS
    function marcarTodos(checkbox) {
        var checkboxes = document.querySelectorAll('.chk-historico');
        for (var i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = checkbox.checked;
        }
        atualizarBotao();
    }

    // 4. EXCLUI SELECIONADOS
    function excluirSelecionados() {
        var checkboxes = document.querySelectorAll('.chk-historico:checked');
        var ids = [];
        for (var i = 0; i < checkboxes.length; i++) {
            ids.push(checkboxes[i].value);
        }
        
        if (ids.length === 0) {
            alert("Nenhum item selecionado.");
            return;
        }
        
        if (!confirm("Excluir " + ids.length + " item(ns) selecionado(s)?")) return;
        
        var btn = document.getElementById('btn-excluir-todos');
        if (btn) btn.disabled = true;
        
        fetch('/excluir_multiplos_relatorio_consolidado', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids: ids})
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) {
                alert("Excluido com sucesso! (" + data.mensagem + ")");
                location.reload();
            } else {
                alert("Erro: " + (data.mensagem || data.erro || "desconhecido"));
            }
        })
        .catch(function(e) {
            alert("Erro na requisicao: " + e);
        });
    }

    // 5. INICIALIZACAO
    window.onload = function() {
        carregarHistorico();
        
        var marcarTodosCheckbox = document.getElementById('selecionar-todos');
        if (marcarTodosCheckbox) {
            marcarTodosCheckbox.onchange = function() {
                marcarTodos(this);
            };
        }
        
        var btnExcluir = document.getElementById('btn-excluir-todos');
        if (btnExcluir) {
            btnExcluir.onclick = excluirSelecionados;
        }
    };
