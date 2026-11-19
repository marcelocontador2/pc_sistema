import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Garantir que a lista de historicos seja carregada ao abrir a pagina
# Procura por window.onload ou DOMContentLoaded
if "window.onload" not in texto and "DOMContentLoaded" not in texto:
    # Insere no final do <script> (antes do </script>)
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + '\n    window.onload = function() { carregarHistorico(); };\n' + texto[pos:]
        print("[OK] window.onload adicionado para carregar historico.")
    else:
        print("[AVISO] Nao encontrei </script>.")
else:
    print("[INFO] window.onload ou DOMContentLoaded ja existe.")

# 2. Garantir que o checkbox tenha a classe e o value corretos
# A linha 232 original:
antigo = """return '<li><input type="checkbox" value="' + h.id + '"><span>Período: ' + h.periodo + '<br><small style="color: #999;">' + (h.data_geracao || 'N/A') + '</small></span></li>';"""
novo = """return '<li><input type="checkbox" class="checkbox-historico" value="' + h.id + '" onchange="atualizarBotaoExcluir()"><span>Período: ' + h.periodo + '<br><small style="color: #999;">' + (h.data_geracao || 'N/A') + '</small></span></li>';"""

if antigo in texto:
    texto = texto.replace(antigo, novo, 1)
    print("[OK] Checkbox com classe e onchange atualizados.")
else:
    # Tenta encontrar de forma mais tolerante
    padrao = re.compile(r"return '<li><input type=\"checkbox\".*?</li>';", re.DOTALL)
    if padrao.search(texto):
        # Substitui o checkbox por um com classe e onchange
        texto = re.sub(r'<input type="checkbox"[^>]*>', '<input type="checkbox" class="checkbox-historico" value="\' + h.id + \'" onchange="atualizarBotaoExcluir()">', texto, count=1)
        print("[OK] Checkbox atualizado (fallback regex).")
    else:
        print("[AVISO] Nao encontrei a linha do checkbox.")

# 3. Adicionar a funcao atualizarBotaoExcluir
if "function atualizarBotaoExcluir" not in texto:
    js = '''
    function atualizarBotaoExcluir() {
        const checkboxes = document.querySelectorAll('.checkbox-historico:checked');
        const btn = document.getElementById('btn-excluir-todos');
        if (btn) {
            btn.disabled = checkboxes.length === 0;
        }
    }
    '''
    pos = texto.rfind('</script>')
    if pos != -1:
        texto = texto[:pos] + js + texto[pos:]
        print("[OK] Funcao atualizarBotaoExcluir adicionada.")
    else:
        print("[AVISO] Nao encontrei </script>.")

# 4. Garantir que o botao Excluir Selecionados comece desabilitado
if 'id="btn-excluir-todos"' in texto and 'disabled' not in texto.split('id="btn-excluir-todos"')[1].split('>')[0]:
    texto = texto.replace(
        '<button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;">Excluir Selecionados</button>',
        '<button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;" disabled>Excluir Selecionados</button>',
        1
    )
    print("[OK] Botao Excluir Selecionados iniciado desabilitado.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
