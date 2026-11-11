import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_checkbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona o botão "Excluir Selecionados" na toolbar
alvo_toolbar = '<button class="btn btn-vermelho" onclick="excluirSelecionado()">Excluir Selecionado</button>'
novo_toolbar = alvo_toolbar + '\n        <button class="btn btn-vermelho" onclick="excluirSelecionadosMultiplos()">Excluir Selecionados</button>'

if alvo_toolbar in html and 'excluirSelecionadosMultiplos' not in html:
    html = html.replace(alvo_toolbar, novo_toolbar, 1)
    print("[OK] Botão 'Excluir Selecionados' adicionado.")

# 2. Altera a função carregarHistorico para incluir checkboxes
alvo_hist = """            data.forEach(item => {
                html += `<div class="historico-item" data-id="${item.id}" onclick="selecionarHistorico(${item.id}, this)">
                    <strong>Período: ${item.periodo}</strong><br>
                    <small style="color:#666;">${item.data_geracao}</small>
                </div>`;
            });"""

novo_hist = """            data.forEach(item => {
                html += `<div class="historico-item" data-id="${item.id}" onclick="selecionarHistorico(${item.id}, this)">
                    <input type="checkbox" class="check-historico" value="${item.id}" onclick="event.stopPropagation();" style="margin-right: 8px; vertical-align: middle;">
                    <strong>Período: ${item.periodo}</strong><br>
                    <small style="color:#666; margin-left: 24px;">${item.data_geracao}</small>
                </div>`;
            });"""

if alvo_hist in html:
    html = html.replace(alvo_hist, novo_hist)
    print("[OK] Checkboxes adicionados ao histórico.")
else:
    # Tenta uma abordagem mais flexível
    padrao = r'(data\.forEach\(item => \{\s*html \+= `<div class="historico-item".*?</div>`;\s*\}\);)'
    match = re.search(padrao, html, re.DOTALL)
    if match:
        html = html.replace(match.group(1), novo_hist)
        print("[OK] Checkboxes adicionados ao histórico (via regex).")
    else:
        print("[AVISO] Bloco do histórico não encontrado no formato esperado.")

# 3. Adiciona a função excluirSelecionadosMultiplos no JavaScript
funcao_excluir_multi = """
function excluirSelecionadosMultiplos() {
    const checkboxes = document.querySelectorAll('.check-historico:checked');
    if (checkboxes.length === 0) {
        alert('Selecione pelo menos um histórico para excluir.');
        return;
    }
    if (!confirm('Excluir ' + checkboxes.length + ' histórico(s) selecionado(s)?')) return;
    
    const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
    let promises = ids.map(id => fetch('/excluir_notas_explicativas/' + id, { method: 'DELETE' }));
    
    Promise.all(promises).then(() => {
        alert('Históricos excluídos com sucesso!');
        carregarHistorico();
        document.getElementById('conteudo').innerHTML = '<p style="text-align:center; color:#666;">Selecione um histórico ou verifique dados.</p>';
        document.getElementById('declaracao-conformidade').style.display = 'none';
    }).catch(err => {
        alert('Erro ao excluir: ' + err.message);
    });
}
"""

if 'function excluirSelecionadosMultiplos' not in html:
    html = html.replace('carregarHistorico();', funcao_excluir_multi + '\ncarregarHistorico();')
    print("[OK] Função 'excluirSelecionadosMultiplos' adicionada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela atualizada.")
