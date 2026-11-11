import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_filtro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona a barra de filtros logo após o título "Notas Explicativas"
filtro_html = """
<div style="background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
    <label style="font-weight: bold; font-size: 13px;">Ano:</label>
    <select id="filtro-ano" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
        <option value="2026">2026</option>
        <option value="2025">2025</option>
    </select>
    <label style="font-weight: bold; font-size: 13px;">Tipo:</label>
    <select id="filtro-tipo" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
        <option value="TRIMESTRE">Trimestral</option>
        <option value="MES">Mensal</option>
    </select>
    <label style="font-weight: bold; font-size: 13px;">Período:</label>
    <select id="filtro-periodo" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
        <option value="1">1º</option>
        <option value="2">2º</option>
        <option value="3">3º</option>
        <option value="4">4º</option>
    </select>
    <button class="btn btn-pdf" onclick="verificarDados()" style="background: #0056b3;">Verificar Dados</button>
    <button class="btn btn-exibir" onclick="salvarDados()" style="background: #28a745;">Salvar</button>
</div>
"""

# Insere o filtro antes da div com class "toolbar"
alvo = '<div class="toolbar">'
if alvo in html:
    html = html.replace(alvo, filtro_html + '\n' + alvo, 1)
    print("[OK] Barra de filtros adicionada.")
else:
    print("[AVISO] Toolbar não encontrada. Inserindo antes do layout.")
    html = html.replace('<div class="layout">', filtro_html + '\n<div class="layout">', 1)

# Adiciona as funções verificarDados e salvarDados no JavaScript
funcoes_js = """
function verificarDados() {
    const ano = document.getElementById('filtro-ano').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const periodo = document.getElementById('filtro-periodo').value;
    const periodoStr = ano + '-' + tipo + '-' + periodo;
    
    document.getElementById('conteudo').innerHTML = '<p style="text-align:center;">Carregando notas explicativas...</p>';
    
    fetch('/api/notas_explicativas/' + periodoStr)
        .then(r => r.json())
        .then(data => {
            if (data.erro) {
                document.getElementById('conteudo').innerHTML = '<p style="color:red; text-align:center;">' + data.mensagem + '</p>';
                return;
            }
            const notas = data.notas || [];
            let html = '';
            notas.forEach(n => {
                html += `<div class="nota"><h3>${n.titulo}</h3><p>${n.texto}</p></div>`;
            });
            document.getElementById('conteudo').innerHTML = html;
            relatorioIdAtual = null; // ainda não foi salvo
        })
        .catch(err => {
            document.getElementById('conteudo').innerHTML = '<p style="color:red;">Erro ao carregar: ' + err.message + '</p>';
        });
}

function salvarDados() {
    const ano = document.getElementById('filtro-ano').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const periodo = document.getElementById('filtro-periodo').value;
    const periodoStr = ano + '-' + tipo + '-' + periodo;
    
    fetch('/salvar_notas_explicativas/' + periodoStr, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                alert('Notas Explicativas salvas com sucesso!');
                carregarHistorico();
            } else {
                alert('Erro ao salvar: ' + data.mensagem);
            }
        });
}
"""

# Insere as funções antes do fechamento do script
alvo_script = 'carregarHistorico();'
if alvo_script in html:
    html = html.replace(alvo_script, funcoes_js + '\n' + alvo_script, 1)
    print("[OK] Funções JavaScript adicionadas.")
else:
    print("[AVISO] Ponto de inserção do script não encontrado.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Tela atualizada com seletor de período.")
