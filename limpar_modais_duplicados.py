import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_limpar_modais_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove TODOS os modais e scripts relacionados (repetidamente até não sobrar nenhum)
while True:
    idx = c.find('<div id="modal-conclusao"')
    if idx == -1:
        break
    # Encontra o fim do script do modal
    fim = c.find('</script>', idx)
    if fim == -1:
        break
    fim += len('</script>')
    c = c[:idx] + c[fim:]

# Remove scripts soltos js-modal-conclusao
c = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# Remove botões antigos duplicados de "Editar Conclusão"
c = re.sub(r'<button[^>]*id="btn-editar-conclusao".*?</button>', '', c, flags=re.DOTALL)

# Re-adiciona o botão ao lado do Gerar PDF
btn_edit = ' <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-left: 10px;">✏️ Editar Conclusão</button>'
match = re.search(r'(<button[^>]*>Gerar PDF</button>)', c, re.IGNORECASE)
if match:
    c = c.replace(match.group(1), match.group(1) + btn_edit, 1)

# Adiciona o NOVO modal (com checkboxes + incluir)
novo_modal = """
<div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
    <div style="background: white; padding: 25px; border-radius: 12px; width: 1000px; max-width: 98%; max-height: 92vh; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        <h3 style="margin: 0 0 10px 0; color: #1a202c;">✏️ Editar Conclusão do Relatório</h3>
        <p style="color: #718096; font-size: 13px; margin: 0 0 15px 0;">Edite os textos, marque "Excluir" para remover do PDF, ou inclua novos blocos abaixo.</p>
        <div id="lista-blocos-modal" style="overflow-y: auto; flex: 1; padding-right: 5px;">
            <div style="text-align:center; padding:40px; color:#999;">Carregando...</div>
        </div>
        <div style="margin-top: 12px; padding: 12px 0; border-top: 1px solid #e2e8f0;">
            <button id="btn-modal-incluir" style="background: #3182ce; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px;">➕ Incluir Novo Bloco</button>
        </div>
        <div style="margin-top: 10px; display: flex; justify-content: flex-end; gap: 10px;">
            <button id="btn-cancelar-conclusao" style="padding: 10px 20px; border: none; border-radius: 6px; background: #e2e8f0; color: #4a5568; font-weight: bold; cursor: pointer;">Cancelar</button>
            <button id="btn-salvar-conclusao-modal" style="padding: 10px 20px; border: none; border-radius: 6px; background: #38a169; color: white; font-weight: bold; cursor: pointer;">💾 Salvar Conclusão</button>
        </div>
    </div>
</div>

<script id="js-modal-conclusao">
document.addEventListener('DOMContentLoaded', function() {
    const btnAbrir = document.getElementById('btn-editar-conclusao');
    const modal = document.getElementById('modal-conclusao');
    const btnCancelar = document.getElementById('btn-cancelar-conclusao');
    const btnSalvar = document.getElementById('btn-salvar-conclusao-modal');
    const btnIncluir = document.getElementById('btn-modal-incluir');
    const lista = document.getElementById('lista-blocos-modal');
    
    const TITULOS_FIXOS = {
        'conclusao-total': '1. Conclusão sobre o Total Executado',
        'conclusao-concentracao': '2. Análise de Concentração',
        'conclusao-alertas': '3. Alertas e Pontos de Atenção',
        'conclusao-recomendacoes': '4. Recomendações'
    };
    
    let blocos = [];
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) { alert("Selecione um histórico."); return; }
        const id = check.value;
        modal.style.display = 'flex';
        lista.innerHTML = '<div style="text-align:center; padding:40px; color:#999;">Carregando textos do relatório...</div>';
        try {
            const res = await fetch(`/historico_centro_custos/${id}`);
            const data = await res.json();
            const dados = data.dados ? data.dados : data;
            let salvo = null;
            if (dados.conclusao_personalizada) {
                try {
                    salvo = typeof dados.conclusao_personalizada === 'string' ? JSON.parse(dados.conclusao_personalizada) : dados.conclusao_personalizada;
                } catch(e) {}
            }
            blocos = [];
            if (salvo && salvo.blocos && Array.isArray(salvo.blocos)) {
                blocos = salvo.blocos.map(b => ({id: b.id, titulo: b.titulo || '', html: b.html || '', excluido: !!b.excluido, extra: !!(b.id && b.id.startsWith('novo-'))}));
            } else if (salvo && Object.keys(salvo).length > 0) {
                Object.entries(TITULOS_FIXOS).forEach(([idB, titulo]) => {
                    blocos.push({id: idB, titulo: titulo, html: salvo[idB] || '', excluido: false, extra: false});
                });
            } else {
                await extrairDoRelatorio(id);
            }
            renderizar();
        } catch(e) { console.error(e); alert("Erro ao carregar."); }
    });
    
    function extrairDoRelatorio(historicoId) {
        return new Promise((resolve) => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `/relatorio_centro_custos?historico_id=${historicoId}&_t=${Date.now()}`;
            document.body.appendChild(iframe);
            setTimeout(() => {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    Object.entries(TITULOS_FIXOS).forEach(([idB, titulo]) => {
                        const el = doc.getElementById(idB);
                        blocos.push({id: idB, titulo: titulo, html: el ? el.innerHTML : '', excluido: false, extra: false});
                    });
                } catch(e) { console.error(e); }
                document.body.removeChild(iframe);
                resolve();
            }, 4000);
        });
    }
    
    function renderizar() {
        lista.innerHTML = '';
        blocos.forEach((bloco, index) => {
            const div = document.createElement('div');
            div.style.cssText = 'border: 1px solid ' + (bloco.excluido ? '#fca5a5' : '#e2e8f0') + '; border-radius: 8px; padding: 12px; margin-bottom: 12px; background: ' + (bloco.excluido ? '#fef2f2' : '#f8fafc') + ';';
            let html = '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">';
            html += '<label style="display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px; color: #718096;"><input type="checkbox" class="bloco-excluir" data-index="' + index + '" ' + (bloco.excluido ? 'checked' : '') + '> Excluir do PDF</label>';
            if (bloco.extra) {
                html += '<input type="text" class="bloco-titulo" data-index="' + index + '" value="' + bloco.titulo.replace(/"/g, '&quot;') + '" style="flex: 1; font-weight: bold; font-size: 14px; padding: 5px; border: 1px solid #cbd5e0; border-radius: 4px;">';
                html += '<button class="bloco-remover" data-index="' + index + '" style="background: #dc2626; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px;">✕ Remover</button>';
            } else {
                html += '<span style="flex: 1; font-weight: bold; font-size: 14px; ' + (bloco.excluido ? 'text-decoration: line-through; color: #999;' : '') + '">' + bloco.titulo + '</span>';
            }
            html += '</div>';
            html += '<div class="bloco-conteudo" contenteditable="' + (bloco.excluido ? 'false' : 'true') + '" data-index="' + index + '" style="min-height: 70px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px; background: #fff; line-height: 1.6; font-size: 14px; ' + (bloco.excluido ? 'pointer-events: none; opacity: 0.5;' : '') + '">' + bloco.html + '</div>';
            div.innerHTML = html;
            lista.appendChild(div);
        });
        lista.querySelectorAll('.bloco-excluir').forEach(chk => chk.addEventListener('change', function() { blocos[parseInt(this.dataset.index)].excluido = this.checked; renderizar(); }));
        lista.querySelectorAll('.bloco-conteudo').forEach(div => div.addEventListener('input', function() { const i = parseInt(this.dataset.index); if (!blocos[i].excluido) blocos[i].html = this.innerHTML; }));
        lista.querySelectorAll('.bloco-titulo').forEach(inp => inp.addEventListener('input', function() { blocos[parseInt(this.dataset.index)].titulo = this.value; }));
        lista.querySelectorAll('.bloco-remover').forEach(btn => btn.addEventListener('click', function() { if (confirm('Remover este bloco?')) { blocos.splice(parseInt(this.dataset.index), 1); renderizar(); } }));
    }
    
    btnIncluir.addEventListener('click', function() {
        blocos.push({id: 'novo-' + Date.now(), titulo: 'Bloco Adicional ' + (blocos.filter(b => b.extra).length + 1), html: '<p>Digite aqui o conteúdo...</p>', excluido: false, extra: true});
        renderizar();
        setTimeout(() => lista.scrollTop = lista.scrollHeight, 100);
    });
    
    btnCancelar.addEventListener('click', function() { modal.style.display = 'none'; });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        const id = check.value;
        const payload = {blocos: blocos.map(b => ({id: b.id, titulo: b.titulo, html: b.html, excluido: b.excluido}))};
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({texto: JSON.stringify(payload)})
            });
            const data = await res.json();
            if (data.erro) alert("Erro: " + data.mensagem);
            else { alert("Salvo! Gere o PDF para ver."); modal.style.display = 'none'; }
        } catch(e) { alert("Erro de conexão."); }
        finally { btnSalvar.innerText = "💾 Salvar Conclusão"; btnSalvar.disabled = false; }
    });
});
</script>
"""

c = c.replace('</body>', novo_modal + '\n</body>', 1)
open(arquivo, 'w', encoding='utf-8').write(c)

# Conta modais
total = c.count('<div id="modal-conclusao"')
print(f"[OK] Modais no arquivo apos limpeza: {total} (deve ser 1)")
print("[OK] Modal unico com checkboxes e botao incluir!")
print()
print("=== TESTE ===")
print("1. Va na tela e aperte Ctrl+F5")
print("2. Marque um historico")
print("3. Clique em 'Editar Conclusao'")
print("4. Voce deve ver: checkbox 'Excluir do PDF' + botao 'Incluir Novo Bloco'")
