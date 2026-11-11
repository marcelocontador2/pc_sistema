import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_checkbox_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona a função que atualiza o históricoSelecionado quando o checkbox é marcado
funcao_checkbox = """
function atualizarSelecaoCheckbox(checkbox) {
    if (checkbox.checked) {
        historicoSelecionado = parseInt(checkbox.value);
        // Marca visualmente a linha como ativa
        document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
        checkbox.closest('.historico-item').classList.add('ativo');
    } else {
        // Se desmarcou, verifica se há outro checkbox marcado
        const outroMarcado = document.querySelector('.check-historico:checked');
        if (outroMarcado) {
            historicoSelecionado = parseInt(outroMarcado.value);
            document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
            outroMarcado.closest('.historico-item').classList.add('ativo');
        } else {
            historicoSelecionado = null;
        }
    }
}
"""

if 'atualizarSelecaoCheckbox' not in html:
    html = html.replace('carregarHistorico();', funcao_checkbox + '\ncarregarHistorico();')
    print("[OK] Função 'atualizarSelecaoCheckbox' adicionada.")

# 2. Altera o checkbox no HTML para chamar a função
html = html.replace(
    'onclick="event.stopPropagation();" style="margin-right: 8px; vertical-align: middle;"',
    'onclick="event.stopPropagation(); atualizarSelecaoCheckbox(this);" style="margin-right: 8px; vertical-align: middle;"'
)

# 3. Atualiza a função excluirSelecionadosMultiplos para recarregar a tela após exclusão
alvo_excluir = """    Promise.all(promises).then(() => {
        alert('Históricos excluídos com sucesso!');
        carregarHistorico();
        document.getElementById('conteudo').innerHTML = '<p style="text-align:center; color:#666;">Selecione um histórico ou verifique dados.</p>';
        document.getElementById('declaracao-conformidade').style.display = 'none';
    })"""

novo_excluir = """    Promise.all(promises).then(() => {
        alert('Históricos excluídos com sucesso!');
        historicoSelecionado = null;
        carregarHistorico();
        document.getElementById('conteudo').innerHTML = '<p style="text-align:center; color:#666;">Clique em "Verificar Dados" para carregar as notas do período selecionado.</p>';
        document.getElementById('declaracao-conformidade').style.display = 'none';
    })"""

if alvo_excluir in html:
    html = html.replace(alvo_excluir, novo_excluir)
    print("[OK] Função de exclusão múltipla atualizada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela corrigida.")
