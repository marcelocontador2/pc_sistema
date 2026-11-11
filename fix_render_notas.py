import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_render_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a função renderizarNotas e substitui por uma versão limpa
padrao = r'(function renderizarNotas\(notas\) \{.*?\n\})'
match = re.search(padrao, html, re.DOTALL)

if match:
    nova_funcao = '''function renderizarNotas(notas) {
    let html = '';
    notas.forEach((n, index) => {
        // Escapa aspas simples no título para não quebrar o JavaScript
        const tituloEscapado = n.titulo.replace(/'/g, "&#39;");
        html += '<div class="nota">';
        html += '<div class="nota-header">';
        html += '<h3>' + n.titulo + '</h3>';
        html += '<div>';
        html += '<button class="btn-edit-nota" onclick="editarNota(' + index + ', \\'' + tituloEscapado + '\\')">✏️ Editar</button>';
        html += '<button class="btn-edit-nota" style="background:#dc3545; color:#fff;" onclick="excluirNota(' + index + ')">🗑️ Excluir</button>';
        html += '</div>';
        html += '</div>';
        html += '<p>' + n.texto + '</p>';
        html += '</div>';
    });
    document.getElementById('conteudo').innerHTML = html;
    document.getElementById('declaracao-conformidade').style.display = 'block';
}'''
    
    html = html.replace(match.group(1), nova_funcao)
    print("[OK] Função renderizarNotas corrigida.")

# Remove a função excluirNota antiga (se existir duplicada)
padrao_excluir = r'function excluirNota\(index\) \{.*?\n\}'
html = re.sub(padrao_excluir, '', html, flags=re.DOTALL)

# Adiciona a função excluirNota correta
funcao_excluir = '''
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
'''

html = html.replace('carregarHistorico();', funcao_excluir + '\ncarregarHistorico();')

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Funções corrigidas.")
