html_novo = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Notas Explicativas</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header-page { background: #fff; padding: 20px 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; border-bottom: 3px solid #003366; }
        .header-page h1 { color: #003366; margin: 0; font-size: 24px; }
        
        .toolbar { display: flex; gap: 10px; margin-bottom: 20px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); flex-wrap: wrap; align-items: center; }
        .toolbar label { font-weight: bold; font-size: 13px; color: #555; }
        .toolbar select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600; transition: 0.2s; }
        .btn-azul { background: #0056b3; color: #fff; }
        .btn-verde { background: #28a745; color: #fff; }
        .btn-vermelho { background: #dc3545; color: #fff; }
        .btn-laranja { background: #ff7f00; color: #fff; }
        .btn-cinza { background: #6c757d; color: #fff; }
        
        .layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
        .sidebar { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: fit-content; }
        .sidebar h3 { color: #003366; margin-top: 0; font-size: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .historico-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; font-size: 13px; border-radius: 4px; transition: 0.2s; }
        .historico-item:hover { background: #f4f8fb; }
        .historico-item.ativo { background: #e3f2fd; border-left: 4px solid #0056b3; font-weight: bold; }
        
        .main-content { background: #fff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); min-height: 600px; }
        .nota { margin-bottom: 30px; page-break-inside: avoid; }
        .nota-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px; margin-bottom: 10px; }
        .nota-header h3 { color: #003366; margin: 0; font-size: 14px; text-transform: uppercase; }
        .nota p { text-align: justify; line-height: 1.6; font-size: 13px; margin: 0; color: #444; }
        
        .btn-edit-nota { background: #ffc107; color: #333; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; }
        .modal-content { background: #fff; padding: 25px; border-radius: 8px; width: 600px; max-width: 90%; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .modal-content h3 { margin-top: 0; color: #003366; }
        .modal-content textarea { width: 100%; height: 150px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 13px; margin-bottom: 15px; box-sizing: border-box; }
        .modal-content input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 15px; box-sizing: border-box; }
        .modal-buttons { text-align: right; }
        
        /* CSS para Impressão */
        @media print {
            body { background: #fff; padding: 0; }
            .container { max-width: 100%; }
            .toolbar, .sidebar, .header-page, .btn-edit-nota { display: none !important; }
            .layout { display: block; }
            .main-content { box-shadow: none; padding: 0; border: none; }
            .nota-header { border-bottom: 2px solid #003366; }
            .nota p { font-size: 11pt; }
            #declaracao-conformidade { page-break-before: always; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header-page">
        <h1>Notas Explicativas</h1>
    </div>

    <div class="toolbar">
        <label>Ano:</label>
        <select id="filtro-ano"><option value="2026">2026</option><option value="2025">2025</option></select>
        <label>Tipo:</label>
        <select id="filtro-tipo"><option value="TRIMESTRE">Trimestral</option><option value="MES">Mensal</option></select>
        <label>Período:</label>
        <select id="filtro-periodo"><option value="1">1º</option><option value="2">2º</option><option value="3">3º</option><option value="4">4º</option></select>
        <button class="btn btn-azul" onclick="verificarDados()">Verificar Dados</button>
        <button class="btn btn-verde" onclick="salvarDados()">Salvar</button>
    </div>

    <div class="toolbar">
        <button class="btn btn-laranja" onclick="window.location.href='/'">← Voltar</button>
        <button class="btn btn-verde" onclick="exibirSelecionado()">Exibir Selecionado</button>
        <button class="btn btn-vermelho" onclick="excluirSelecionado()">Excluir Selecionado</button>
        <button class="btn btn-azul" onclick="gerarPDFHistorico()">Gerar PDF</button>
        <button class="btn btn-azul" onclick="abrirObservacoes()">Observações</button>
        <button class="btn btn-azul" onclick="abrirConclusao()">Conclusão</button>
    </div>

    <div class="layout">
        <div class="sidebar">
            <h3>Histórico Salvo</h3>
            <div id="lista-historico">Carregando...</div>
        </div>
        <div class="main-content" id="conteudo">
            <p style="text-align:center; color:#666;">Clique em "Verificar Dados" para carregar as notas do período selecionado.</p>
        </div>
    </div>

    <div id="declaracao-conformidade" style="display: none; margin-top: 40px; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 5px solid #003366;">
        <h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-top: 0; margin-bottom: 20px; font-size: 15px; text-transform: uppercase;">Declaração de Conformidade</h3>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;">Declaramos, na qualidade de responsáveis pela gestão e pela elaboração das demonstrações contábeis consolidadas do Conselho Federal de Enfermagem (COFEN), referentes ao período de 01/01/2026 a 30/09/2026 (2026-TRIMESTRE-3), que:</p>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>1.</b> As informações contábeis foram elaboradas em conformidade com as disposições da Lei nº 4.320/1964, as diretrizes do Manual de Contabilidade Aplicada ao Setor Público (MCASP) e as Normas Brasileiras de Contabilidade Técnicas do Setor Público (NBC TSP).</p>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>2.</b> As demonstrações contábeis consolidadas (Balanço Patrimonial, Balanço Orçamentário, Balanço Financeiro, Demonstração das Variações Patrimoniais, Demonstração dos Fluxos de Caixa e Demonstração das Mutações do Patrimônio Líquido) refletem, de forma fidedigna, a posição patrimonial e financeira do COFEN e o desempenho da execução orçamentária no período.</p>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>3.</b> Os registros contábeis estão amparados em documentação de suporte idônea e devidamente auditada internamente, observando os princípios da legalidade, da transparência, da economicidade e da segregação de funções.</p>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>4.</b> As práticas de gestão de riscos, os controles internos administrativos e o processo de conformidade foram implementados e mantidos operantes durante todo o período analisado, garantindo a integridade dos dados apresentados.</p>
        <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;"><b>5.</b> Esta declaração é firmada com base nas informações extraídas dos sistemas corporativos e validadas pelos responsáveis técnicos, nos termos da Resolução COFEN nº 764/2024 (Prestação de Contas).</p>
        
        <div style="margin-top: 50px; text-align: center;">
            <p style="margin: 0; font-size: 14px; font-weight: bold; color: #003366;" id="nome-contador">Carregando...</p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">CRC: <span id="crc-contador">...</span></p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">CPF: <span id="cpf-contador">...</span></p>
        </div>
    </div>
</div>

<!-- Modal Observações -->
<div class="modal" id="modal-obs">
    <div class="modal-content">
        <h3>Nova Observação</h3>
        <label style="font-weight:bold; font-size:13px;">Item (Número da Nota):</label>
        <input type="number" id="obs-item" min="1" max="20" value="1">
        <label style="font-weight:bold; font-size:13px;">Texto da Observação:</label>
        <textarea id="obs-texto" placeholder="Digite a observação..."></textarea>
        <div class="modal-buttons">
            <button class="btn btn-cinza" onclick="fecharModal('modal-obs')">Cancelar</button>
            <button class="btn btn-verde" onclick="salvarObservacao()">Salvar</button>
        </div>
    </div>
</div>

<!-- Modal Conclusão -->
<div class="modal" id="modal-concl">
    <div class="modal-content">
        <h3>Conclusão</h3>
        <textarea id="concl-texto" placeholder="Digite a conclusão..."></textarea>
        <div class="modal-buttons">
            <button class="btn btn-cinza" onclick="fecharModal('modal-concl')">Cancelar</button>
            <button class="btn btn-verde" onclick="salvarConclusao()">Salvar</button>
        </div>
    </div>
</div>

<!-- Modal Edição de Nota -->
<div class="modal" id="modal-edit-nota">
    <div class="modal-content">
        <h3 id="titulo-edit-nota">Editar Nota</h3>
        <textarea id="edit-nota-texto" placeholder="Digite o texto da nota..." style="height: 200px;"></textarea>
        <div class="modal-buttons">
            <button class="btn btn-cinza" onclick="fecharModal('modal-edit-nota')">Cancelar</button>
            <button class="btn btn-verde" onclick="salvarNotaEditada()">Salvar</button>
        </div>
    </div>
</div>

<script>
let historicoSelecionado = null;
let relatorioIdAtual = null;
let notaEditandoIndex = null;
let notasAtuais = [];

function fecharModal(id) { document.getElementById(id).style.display = 'none'; }

function formatarCPF(cpf) {
    if (!cpf) return '';
    let limpo = cpf.replace(/[^0-9]/g, '');
    if (limpo.length === 11) {
        return '***.' + limpo.substring(3,6) + '.***-**';
    }
    return cpf;
}

function formatarCRC(crc, uf) {
    if (!crc) return '';
    let limpo = crc.replace(/[^A-Z0-9]/g, '').toUpperCase();
    if (limpo.length === 11) {
        let u = uf || limpo.substring(0,2);
        return limpo.substring(0,2) + '-' + limpo.substring(2,8) + '/' + limpo.substring(8,9) + '-' + limpo.substring(9);
    }
    return crc;
}

function carregarHistorico() {
    fetch('/historico_notas_explicativas')
        .then(r => r.json())
        .then(data => {
            const div = document.getElementById('lista-historico');
            if (!data || data.length === 0) {
                div.innerHTML = '<p style="font-size:13px; color:#999; text-align:center;">Nenhum histórico salvo.</p>';
                return;
            }
            let html = '';
            data.forEach(item => {
                html += `<div class="historico-item" data-id="${item.id}" onclick="selecionarHistorico(${item.id}, this)">
                    <strong>Período: ${item.periodo}</strong><br>
                    <small style="color:#666;">${item.data_geracao}</small>
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
                document.getElementById('conteudo').innerHTML = '<p style="color:red; text-align:center;">' + data.erro + '</p>';
                return;
            }
            relatorioIdAtual = id;
            notasAtuais = data.dados.notas || [];
            renderizarNotas(notasAtuais);
            carregarDadosContador();
        });
}

function renderizarNotas(notas) {
    let html = '';
    notas.forEach((n, index) => {
        html += `<div class="nota">
            <div class="nota-header">
                <h3>${n.titulo}</h3>
                <button class="btn-edit-nota" onclick="editarNota(${index}, '${n.titulo.replace(/'/g, "\\\\'")}')">✏️ Editar</button>
            </div>
            <p>${n.texto}</p>
        </div>`;
    });
    document.getElementById('conteudo').innerHTML = html;
    document.getElementById('declaracao-conformidade').style.display = 'block';
}

function verificarDados() {
    const ano = document.getElementById('filtro-ano').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const periodo = document.getElementById('filtro-periodo').value;
    const periodoStr = ano + '-' + tipo + '-' + periodo;
    
    document.getElementById('conteudo').innerHTML = '<p style="text-align:center; color:#0056b3;">Carregando notas explicativas...</p>';
    document.getElementById('declaracao-conformidade').style.display = 'none';
    
    fetch('/api/notas_explicativas/' + periodoStr)
        .then(r => r.json())
        .then(data => {
            if (data.erro) {
                document.getElementById('conteudo').innerHTML = '<p style="color:red; text-align:center;">' + data.mensagem + '</p>';
                return;
            }
            notasAtuais = data.notas || [];
            renderizarNotas(notasAtuais);
            carregarDadosContador();
            relatorioIdAtual = null;
        })
        .catch(err => {
            document.getElementById('conteudo').innerHTML = '<p style="color:red; text-align:center;">Erro ao carregar: ' + err.message + '</p>';
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
    if (!historicoSelecionado) { alert('Selecione um histórico primeiro.'); return; }
    carregarNotas(historicoSelecionado);
}

function gerarPDFHistorico() {
    if (!historicoSelecionado) { alert('Selecione um histórico primeiro.'); return; }
    window.open('/gerar_pdf_notas/' + historicoSelecionado, '_blank');
}

function excluirSelecionado() {
    if (!historicoSelecionado) { alert('Selecione um histórico.'); return; }
    if (!confirm('Excluir este histórico?')) return;
    fetch('/excluir_notas_explicativas/' + historicoSelecionado, { method: 'DELETE' })
        .then(r => r.json())
        .then(() => { 
            historicoSelecionado = null; 
            relatorioIdAtual = null; 
            carregarHistorico(); 
            document.getElementById('conteudo').innerHTML = '<p style="text-align:center; color:#666;">Histórico excluído.</p>'; 
            document.getElementById('declaracao-conformidade').style.display = 'none';
        });
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

function editarNota(index, titulo) {
    notaEditandoIndex = index;
    document.getElementById('titulo-edit-nota').innerText = 'Editar: ' + titulo;
    const notasElements = document.querySelectorAll('.nota p');
    if (notasElements[index]) {
        document.getElementById('edit-nota-texto').value = notasElements[index].innerText;
    }
    document.getElementById('modal-edit-nota').style.display = 'flex';
}

function salvarNotaEditada() {
    const novoTexto = document.getElementById('edit-nota-texto').value;
    if (!notaEditandoIndex && notaEditandoIndex !== 0) return;
    
    if (relatorioIdAtual) {
        fetch('/api/editar_nota/' + relatorioIdAtual + '/' + notaEditandoIndex, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: novoTexto })
        }).then(r => r.json()).then(data => {
            if (data.ok) {
                notasAtuais[notaEditandoIndex].texto = novoTexto;
                renderizarNotas(notasAtuais);
                fecharModal('modal-edit-nota');
                alert('Nota atualizada!');
            } else {
                alert('Erro: ' + data.mensagem);
            }
        });
    } else {
        notasAtuais[notaEditandoIndex].texto = novoTexto;
        renderizarNotas(notasAtuais);
        fecharModal('modal-edit-nota');
        alert('Nota atualizada (não salva no histórico).');
    }
}

function carregarDadosContador() {
    fetch('/api/configuracoes/entidade')
        .then(r => r.json())
        .then(data => {
            if (data.contador_nome) document.getElementById('nome-contador').innerText = data.contador_nome;
            if (data.contador_crc) document.getElementById('crc-contador').innerText = formatarCRC(data.contador_crc, data.contador_uf);
            if (data.contador_cpf) document.getElementById('cpf-contador').innerText = formatarCPF(data.contador_cpf);
        });
}

carregarHistorico();
</script>
</body>
</html>
"""

with open(r"pc_frontend\notas_explicativas.html", "w", encoding="utf-8") as f:
    f.write(html_novo)
print("[OK] Tela notas_explicativas.html refeita com layout premium e funcionalidades completas.")
