import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Substitui o checkbox "Marcar Todos" para chamar a funcao marcarTodos(this) diretamente
antigo_marcar = '<label style="cursor:pointer;"><input type="checkbox" id="selecionar-todos" onclick="marcarTodos(this)"> Marcar Todos</label>'
novo_marcar = '<label style="cursor:pointer;"><input type="checkbox" id="selecionar-todos" onclick="marcarTodos(this)"> Marcar Todos</label>'
if antigo_marcar in texto:
    print("[INFO] Checkbox 'Marcar Todos' ja tem onclick.")
else:
    # Se nao tem, procura e adiciona
    texto = texto.replace('<input type="checkbox" id="selecionar-todos"', '<input type="checkbox" id="selecionar-todos" onclick="marcarTodos(this)"', 1)
    print("[OK] onclick adicionado ao 'Marcar Todos'.")

# 2. Substitui o botao "Excluir Selecionados" para chamar a funcao excluirSelecionados() diretamente
antigo_botao = '<button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;" disabled>Excluir Selecionados</button>'
novo_botao = '<button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;" disabled>Excluir Selecionados</button>'
if antigo_botao in texto:
    print("[INFO] Botao 'Excluir Selecionados' ja tem onclick.")
else:
    # Se nao tem, procura e adiciona
    texto = texto.replace('<button id="btn-excluir-todos"', '<button id="btn-excluir-todos" onclick="excluirSelecionados()"', 1)
    print("[OK] onclick adicionado ao 'Excluir Selecionados'.")

# 3. Garante que a funcao marcarTodos exista no script
if "function marcarTodos" not in texto:
    js = '''
    function marcarTodos(checkbox) {
        var checkboxes = document.querySelectorAll('.chk-historico');
        for (var i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = checkbox.checked;
        }
        atualizarBotao();
    }
    '''
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + js + texto[pos:]
        print("[OK] Funcao marcarTodos adicionada.")
    else:
        print("[AVISO] Nao encontrei </script>.")
else:
    print("[INFO] Funcao marcarTodos ja existe.")

# 4. Garante que a funcao excluirSelecionados exista
if "function excluirSelecionados" not in texto:
    js = '''
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
        
        fetch('/excluir_multiplos_relatorio_consolidado', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids: ids})
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) {
                alert("Excluido com sucesso!");
                location.reload();
            } else {
                alert("Erro: " + (data.mensagem || data.erro || "desconhecido"));
            }
        })
        .catch(function(e) {
            alert("Erro na requisicao: " + e);
        });
    }
    '''
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + js + texto[pos:]
        print("[OK] Funcao excluirSelecionados adicionada.")
    else:
        print("[AVISO] Nao encontrei </script>.")
else:
    print("[INFO] Funcao excluirSelecionados ja existe.")

# 5. Garante que atualizarBotao exista
if "function atualizarBotao" not in texto:
    js = '''
    function atualizarBotao() {
        var btn = document.getElementById('btn-excluir-todos');
        if (!btn) return;
        var checkboxes = document.querySelectorAll('.chk-historico:checked');
        btn.disabled = (checkboxes.length === 0);
    }
    '''
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + js + texto[pos:]
        print("[OK] Funcao atualizarBotao adicionada.")
    else:
        print("[AVISO] Nao encontrei </script>.")
else:
    print("[INFO] Funcao atualizarBotao ja existe.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
