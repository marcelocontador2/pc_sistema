import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_excluir_nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Altera a função renderizarNotas para adicionar o botão de excluir
alvo_render = """            html += `<div class="nota">
                <div class="nota-header">
                    <h3>${n.titulo}</h3>
                    <button class="btn-edit-nota" onclick="editarNota(${index}, '${n.titulo.replace(/'/g, "\\\\'")}')">✏️ Editar</button>
                </div>
                <p>${n.texto}</p>
            </div>`;"""

novo_render = """            html += `<div class="nota">
                <div class="nota-header">
                    <h3>${n.titulo}</h3>
                    <div>
                        <button class="btn-edit-nota" onclick="editarNota(${index}, '${n.titulo.replace(/'/g, "\\\\'")}')">✏️ Editar</button>
                        <button class="btn-edit-nota" style="background:#dc3545; color:#fff;" onclick="excluirNota(${index})">🗑️ Excluir</button>
                    </div>
                </div>
                <p>${n.texto}</p>
            </div>`;"""

if alvo_render in html:
    html = html.replace(alvo_render, novo_render)
    print("[OK] Botão de excluir adicionado às notas.")
else:
    print("[AVISO] Bloco renderizarNotas não encontrado no formato esperado.")

# 2. Adiciona a função excluirNota no JavaScript
funcao_excluir = """
function excluirNota(index) {
    if (!relatorioIdAtual) {
        alert('Selecione um histórico primeiro.');
        return;
    }
    if (!confirm('Excluir esta nota?')) return;
    
    fetch('/api/excluir_nota/' + relatorioIdAtual + '/' + index, {
        method: 'DELETE'
    }).then(r => r.json()).then(data => {
        if (data.ok) {
            alert('Nota excluída!');
            carregarNotas(relatorioIdAtual);
        } else {
            alert('Erro: ' + data.mensagem);
        }
    });
}
"""

if 'function excluirNota' not in html:
    html = html.replace('carregarHistorico();', funcao_excluir + '\ncarregarHistorico();')
    print("[OK] Função excluirNota adicionada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela atualizada.")
