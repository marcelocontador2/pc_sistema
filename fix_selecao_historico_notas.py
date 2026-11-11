import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_fix_selecao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Corrige a função selecionarHistorico
alvo_sel = """function selecionarHistorico(id, el) {
    historicoSelecionado = id;
    document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
    el.classList.add('ativo');
    carregarNotas(id);
}"""

novo_sel = """function selecionarHistorico(id, el) {
    historicoSelecionado = id;
    document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
    el.classList.add('ativo');
    // Marca o checkbox correspondente
    const check = el.querySelector('.check-historico');
    if (check) check.checked = true;
    carregarNotas(id);
}"""

if alvo_sel in html:
    html = html.replace(alvo_sel, novo_sel)
    print("[OK] Função selecionarHistorico corrigida.")
else:
    print("[AVISO] Função selecionarHistorico não encontrada no formato esperado.")

# 2. Corrige a função atualizarSelecaoCheckbox (garante que o histórico seja atualizado)
alvo_check = """function atualizarSelecaoCheckbox(checkbox) {
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
}"""

novo_check = """function atualizarSelecaoCheckbox(checkbox) {
    if (checkbox.checked) {
        historicoSelecionado = parseInt(checkbox.value);
        document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
        checkbox.closest('.historico-item').classList.add('ativo');
    } else {
        const outroMarcado = document.querySelector('.check-historico:checked');
        if (outroMarcado) {
            historicoSelecionado = parseInt(outroMarcado.value);
            document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
            outroMarcado.closest('.historico-item').classList.add('ativo');
        } else {
            historicoSelecionado = null;
        }
    }
}"""

if alvo_check in html:
    html = html.replace(alvo_check, novo_check)
    print("[OK] Função atualizarSelecaoCheckbox corrigida.")
else:
    print("[AVISO] Função atualizarSelecaoCheckbox não encontrada no formato esperado.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela corrigida.")
