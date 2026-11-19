import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")

if not arquivo.exists():
    print("[ERRO] Arquivo nao encontrado:", arquivo)
    sys.exit(1)

# Backup
import shutil
backup = arquivo.with_suffix(".html.bak")
shutil.copy2(arquivo, backup)
print(f"[OK] Backup criado: {backup}")

texto = arquivo.read_text(encoding="utf-8")

# 1. Adicionar checkbox "Selecionar Todos" antes da lista
# Procura o titulo "Historico Salvo" (ou similar) para injetar o checkbox
if "selecionar-todos" not in texto:
    # Procura a div que contem os checkboxes individuais
    # Vamos inserir antes da primeira ocorrencia de <div id="lista-historico" ou similar
    # Se nao encontrar, inserimos no inicio do body
    if '<div id="lista-historico"' in texto:
        texto = texto.replace(
            '<div id="lista-historico"',
            '''<div style="margin-bottom: 10px;">
                <label style="cursor:pointer; font-weight:bold;">
                    <input type="checkbox" id="selecionar-todos" onclick="marcarTodos(this)"> Selecionar Todos
                </label>
            </div>
            <div id="lista-historico"''',
            1
        )
    elif 'Histórico Salvo' in texto:
        texto = texto.replace(
            'Histórico Salvo',
            '''Histórico Salvo
            <div style="margin: 5px 0; font-size: 12px;">
                <label style="cursor:pointer;"><input type="checkbox" id="selecionar-todos" onclick="marcarTodos(this)"> Marcar Todos</label>
            </div>''',
            1
        )
    print("[OK] Checkbox 'Selecionar Todos' adicionado.")
else:
    print("[INFO] Checkbox 'Selecionar Todos' ja existe.")

# 2. Adicionar botao "Excluir Selecionados"
if "excluir-selecionados" not in texto:
    # Procura o botao "Excluir Selecionado" (singular) e adiciona um novo ao lado
    if 'Excluir Selecionado' in texto:
        texto = texto.replace(
            'Excluir Selecionado',
            'Excluir Selecionado</button><button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;">Excluir Selecionados</button>',
            1
        )
    print("[OK] Botao 'Excluir Selecionados' adicionado.")
else:
    print("[INFO] Botao 'Excluir Selecionados' ja existe.")

# 3. Adicionar funcoes JavaScript
if "function marcarTodos" not in texto:
    # Injeta antes do </script> final (ou antes de </body>)
    js = '''
    function marcarTodos(checkbox) {
        const checkboxes = document.querySelectorAll('.checkbox-historico');
        checkboxes.forEach(cb => cb.checked = checkbox.checked);
    }

    function excluirSelecionados() {
        const checkboxes = document.querySelectorAll('.checkbox-historico:checked');
        const ids = Array.from(checkboxes).map(cb => cb.value);
        
        if (ids.length === 0) {
            alert('Nenhum item selecionado.');
            return;
        }
        
        if (!confirm(`Excluir ${ids.length} item(ns)?`)) return;
        
        fetch('/excluir_multiplos_relatorio_consolidado', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids: ids})
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                alert('Itens excluídos!');
                location.reload();
            } else {
                alert('Erro: ' + (data.mensagem || 'desconhecido'));
            }
        })
        .catch(e => alert('Erro: ' + e));
    }
    '''
    # Insere antes do ultimo </script>
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + js + texto[pos:]
        print("[OK] Funcoes JavaScript adicionadas.")
    else:
        print("[AVISO] Nao encontrei </script> para injetar as funcoes.")
else:
    print("[INFO] Funcoes JavaScript ja existem.")

# Salva
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo HTML atualizado.")
