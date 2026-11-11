import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_edicao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona o CSS para os botões de edição e o modal
css_extra = """
<style>
.btn-edit-nota { background: #ffc107; color: #333; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; margin-left: 10px; }
.nota-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.nota-header h3 { margin: 0; }
</style>
"""

if 'btn-edit-nota' not in html:
    html = html.replace('</head>', css_extra + '</head>')

# 2. Altera a função carregarNotas para incluir o botão de edição
alvo_carregar = """            notas.forEach(n => {
                html += `<div class="nota"><h3>${n.titulo}</h3><p>${n.texto}</p></div>`;
            });"""

novo_carregar = """            notas.forEach((n, index) => {
                html += `<div class="nota">
                    <div class="nota-header">
                        <h3>${n.titulo}</h3>
                        <button class="btn-edit-nota" onclick="editarNota(${index}, '${n.titulo.replace(/'/g, "\\\\'")}')">✏️ Editar</button>
                    </div>
                    <p id="texto-nota-${index}">${n.texto}</p>
                </div>`;
            });"""

if alvo_carregar in html:
    html = html.replace(alvo_carregar, novo_carregar)
    print("[OK] Botão de edição adicionado às notas.")

# 3. Adiciona o modal de edição de nota
modal_edicao = """
<!-- Modal Edição de Nota -->
<div class="modal" id="modal-edit-nota">
    <div class="modal-content">
        <h3 id="titulo-edit-nota">Editar Nota</h3>
        <textarea id="edit-nota-texto" placeholder="Digite o texto da nota..." style="height: 200px;"></textarea>
        <div class="modal-buttons">
            <button class="btn btn-excluir" onclick="fecharModal('modal-edit-nota')">Cancelar</button>
            <button class="btn btn-exibir" onclick="salvarNotaEditada()">Salvar</button>
        </div>
    </div>
</div>
"""

if 'modal-edit-nota' not in html:
    html = html.replace('</body>', modal_edicao + '</body>')

# 4. Adiciona as funções de edição no JavaScript (antes do carregarHistorico)
funcoes_edicao = """
let notaEditandoIndex = null;

function editarNota(index, titulo) {
    notaEditandoIndex = index;
    document.getElementById('titulo-edit-nota').innerText = 'Editar: ' + titulo;
    const textoAtual = document.getElementById('texto-nota-' + index).innerText;
    document.getElementById('edit-nota-texto').value = textoAtual;
    document.getElementById('modal-edit-nota').style.display = 'flex';
}

function salvarNotaEditada() {
    const novoTexto = document.getElementById('edit-nota-texto').value;
    if (!notaEditandoIndex && notaEditandoIndex !== 0) return;
    
    if (relatorioIdAtual) {
        // Salva no banco via API
        fetch('/api/editar_nota/' + relatorioIdAtual + '/' + notaEditandoIndex, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: novoTexto })
        }).then(r => r.json()).then(data => {
            if (data.ok) {
                document.getElementById('texto-nota-' + notaEditandoIndex).innerText = novoTexto;
                fecharModal('modal-edit-nota');
                alert('Nota atualizada!');
            } else {
                alert('Erro: ' + data.mensagem);
            }
        });
    } else {
        // Apenas atualiza visualmente (nota ainda não salva)
        document.getElementById('texto-nota-' + notaEditandoIndex).innerText = novoTexto;
        fecharModal('modal-edit-nota');
        alert('Nota atualizada (não salva no histórico).');
    }
}
"""

if 'function editarNota' not in html:
    html = html.replace('carregarHistorico();', funcoes_edicao + '\ncarregarHistorico();')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Funcionalidade de edição adicionada.")
