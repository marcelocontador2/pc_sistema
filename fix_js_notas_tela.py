import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_fix_js_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Encontra o bloco <script> e substitui todas as funções
# Primeiro, localiza o script existente
padrao_script = r'(<script>.*?</script>)'
match = re.search(padrao_script, html, re.DOTALL)

if match:
    script_antigo = match.group(1)
    
    novo_script = '''<script>
let historicoSelecionado = null;
let relatorioIdAtual = null;

function fecharModal(id) { document.getElementById(id).style.display = 'none'; }

function carregarHistorico() {
    fetch('/historico_notas_explicativas')
        .then(r => r.json())
        .then(data => {
            const div = document.getElementById('lista-historico');
            if (!data || data.length === 0) {
                div.innerHTML = '<p style="font-size:12px; color:#999;">Nenhum histórico salvo.</p>';
                return;
            }
            let html = '';
            data.forEach(item => {
                html += `<div class="historico-item" data-id="${item.id}" onclick="selecionarHistorico(${item.id}, this)">
                    <strong>Período: ${item.periodo}</strong><br>
                    <small>Gerado em: ${item.data_geracao}</small>
                </div>`;
            });
            div.innerHTML = html;
        });
}

function selecionarHistorico(id, el) {
    historicoSelecionado = id;
    document.querySelectorAll('.historico-item').forEach(i => i.classList.remove('ativo'));
    el.classList.add('ativo');
    carregarNotas(id);
}

function carregarNotas(id) {
    fetch('/historico_notas_explicativas/' + id)
        .then(r => r.json())
        .then(data => {
            if (data.erro) {
                document.getElementById('conteudo').innerHTML = '<p style="color:red;">' + data.erro + '</p>';
                return;
            }
            relatorioIdAtual = id;
            const notas = data.dados.notas || [];
            let html = '';
            notas.forEach(n => {
                html += `<div class="nota"><h3>${n.titulo}</h3><p>${n.texto}</p></div>`;
            });
            document.getElementById('conteudo').innerHTML = html;
        });
}

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
            relatorioIdAtual = null;
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

function exibirSelecionado() {
    if (!historicoSelecionado) {
        alert('Selecione um histórico primeiro.');
        return;
    }
    carregarNotas(historicoSelecionado);
}

function gerarPDFHistorico() {
    if (!historicoSelecionado) {
        alert('Selecione um histórico primeiro.');
        return;
    }
    window.open('/gerar_pdf_notas/' + historicoSelecionado, '_blank');
}

function excluirSelecionado() {
    if (!historicoSelecionado) { alert('Selecione um histórico.'); return; }
    if (!confirm('Excluir este histórico?')) return;
    fetch('/excluir_notas_explicativas/' + historicoSelecionado, { method: 'DELETE' })
        .then(r => r.json())
        .then(() => { historicoSelecionado = null; relatorioIdAtual = null; carregarHistorico(); document.getElementById('conteudo').innerHTML = ''; });
}

function abrirObservacoes() {
    if (!relatorioIdAtual) { alert('Selecione um histórico.'); return; }
    document.getElementById('modal-obs').style.display = 'flex';
}

function salvarObservacao() {
    const item = document.getElementById('obs-item').value;
    const texto = document.getElementById('obs-texto').value;
    if (!texto.trim()) { alert('Digite o texto.'); return; }
    fetch('/api/observacoes_notas/' + relatorioIdAtual, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item, texto })
    }).then(r => r.json()).then(() => {
        alert('Observação salva!');
        fecharModal('modal-obs');
        document.getElementById('obs-texto').value = '';
    });
}

function abrirConclusao() {
    if (!relatorioIdAtual) { alert('Selecione um histórico.'); return; }
    fetch('/api/conclusao_notas/' + relatorioIdAtual)
        .then(r => r.json())
        .then(data => {
            document.getElementById('concl-texto').value = data.texto || '';
            document.getElementById('modal-concl').style.display = 'flex';
        });
}

function salvarConclusao() {
    const texto = document.getElementById('concl-texto').value;
    fetch('/api/conclusao_notas/' + relatorioIdAtual, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
    }).then(r => r.json()).then(() => {
        alert('Conclusão salva!');
        fecharModal('modal-concl');
    });
}

carregarHistorico();
</script>'''
    
    html = html.replace(script_antigo, novo_script)
    with open(ARQ, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Script da tela Notas Explicativas reescrito com todas as funções.")
else:
    print("[ERRO] Script não encontrado no HTML.")
