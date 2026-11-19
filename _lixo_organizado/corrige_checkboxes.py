import sys
from pathlib import Path
import shutil

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")

# Backup
shutil.copy2(arquivo, arquivo.with_suffix(".html.bak2"))
print("[OK] Backup criado: relatorio_consolidado.html.bak2")

texto = arquivo.read_text(encoding="utf-8")

# 1. Adicionar a classe 'checkbox-historico' nos checkboxes criados dinamicamente
antigo = """<li><input type="checkbox" value="' + h.id + '"><span>Período: ' + h.periodo + '<br><small style="color: #999;">' + (h.data_geracao || 'N/A') + '</small></span></li>"""
novo = """<li><input type="checkbox" class="checkbox-historico" value="' + h.id + '"><span>Período: ' + h.periodo + '<br><small style="color: #999;">' + (h.data_geracao || 'N/A') + '</small></span></li>"""

if antigo in texto:
    texto = texto.replace(antigo, novo, 1)
    print("[OK] Classe 'checkbox-historico' adicionada nos checkboxes.")
else:
    print("[AVISO] Nao encontrei a linha exata dos checkboxes.")

# 2. Corrigir o botao com </button> sobrando
antigo_botao = """<button class="btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button><button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;">Excluir Selecionados</button></button>"""
novo_botao = """<button class="btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button><button id="btn-excluir-todos" onclick="excluirSelecionados()" class="btn btn-danger" style="margin-left:5px;">Excluir Selecionados</button>"""

if antigo_botao in texto:
    texto = texto.replace(antigo_botao, novo_botao, 1)
    print("[OK] </button> extra removido do botao.")
else:
    print("[AVISO] Nao encontrei o bloco do botao para corrigir.")

# 3. Garantir que o checkbox "Selecionar Todos" tambem use a classe nos checkboxes
# (o onclick chama marcarTodos(this) que ja esta correto)

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
