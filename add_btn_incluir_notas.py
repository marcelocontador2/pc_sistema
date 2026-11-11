import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_btn_include_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove o botão "Excluir Selecionado"
html = html.replace('<button class="btn btn-vermelho" onclick="excluirSelecionado()">Excluir Selecionado</button>\n        ', '')
html = html.replace('<button class="btn btn-vermelho" onclick="excluirSelecionado()">Excluir Selecionado</button>', '')

# 2. Adiciona o botão "Incluir Item" na toolbar (ao lado de Gerar PDF)
alvo_toolbar = '<button class="btn btn-azul" onclick="gerarPDFHistorico()">Gerar PDF</button>'
novo_toolbar = alvo_toolbar + '\n        <button class="btn btn-verde" onclick="abrirInclusao()">Incluir Item</button>'

if alvo_toolbar in html and 'abrirInclusao' not in html:
    html = html.replace(alvo_toolbar, novo_toolbar, 1)
    print("[OK] Botão 'Incluir Item' adicionado.")

# 3. Adiciona o Modal de Inclusão
modal_inclusao = """
<!-- Modal Incluir Item -->
<div class="modal" id="modal-incluir">
    <div class="modal-content">
        <h3>Incluir Nova Nota Explicativa</h3>
        <label style="font-weight:bold; font-size:13px;">Título da Nota:</label>
        <input type="text" id="incluir-titulo" placeholder="Ex: NOTA 16 – NOVO ITEM" style="width:100%; padding:8px; margin-bottom:15px; border:1px solid #ccc; border-radius:4px; box-sizing:border-box;">
        <label style="font-weight:bold; font-size:13px;">Texto da Nota:</label>
        <textarea id="incluir-texto" placeholder="Digite o texto da nota..." style="width:100%; height:150px; padding:10px; border:1px solid #ccc; border-radius:4px; font-family:inherit; margin-bottom:15px; box-sizing:border-box;"></textarea>
        <div class="modal-buttons">
            <button class="btn btn-cinza" onclick="fecharModal('modal-incluir')">Cancelar</button>
            <button class="btn btn-verde" onclick="salvarNovaNota()">Adicionar</button>
        </div>
    </div>
</div>
"""

if 'modal-incluir' not in html:
    html = html.replace('</body>', modal_inclusao + '</body>')
    print("[OK] Modal de inclusão adicionado.")

# 4. Adiciona as funções JS
funcoes_js = """
function abrirInclusao() {
    if (!relatorioIdAtual) {
        alert('Selecione um histórico primeiro para adicionar uma nota.');
        return;
    }
    document.getElementById('incluir-titulo').value = '';
    document.getElementById('incluir-texto').value = '';
    document.getElementById('modal-incluir').style.display = 'flex';
}

function salvarNovaNota() {
    const titulo = document.getElementById('incluir-titulo').value.trim();
    const texto = document.getElementById('incluir-texto').value.trim();
    if (!titulo || !texto) {
        alert('Preencha o título e o texto.');
        return;
    }
    fetch('/api/incluir_nota/' + relatorioIdAtual, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, texto })
    }).then(r => r.json()).then(data => {
        if (data.ok) {
            alert('Nota incluída com sucesso!');
            fecharModal('modal-incluir');
            carregarNotas(relatorioIdAtual);
        } else {
            alert('Erro: ' + data.mensagem);
        }
    });
}
"""

if 'function abrirInclusao' not in html:
    html = html.replace('carregarHistorico();', funcoes_js + '\ncarregarHistorico();')
    print("[OK] Funções de inclusão adicionadas.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela atualizada.")
