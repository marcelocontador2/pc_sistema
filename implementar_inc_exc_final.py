import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. MODAL NA TELA PRINCIPAL
# ==========================================
main_path = r"pc_frontend\analise_centro_custos.html"
shutil.copy2(main_path, f"{main_path}.bak_final_inc_exc_{ts}")
c = open(main_path, encoding='utf-8').read()

# Remove modal antigo
c = re.sub(r'<div id="modal-conclusao".*?</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# Novo modal
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
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
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
                    salvo = typeof dados.conclusao_personalizada === 'string' 
                        ? JSON.parse(dados.conclusao_personalizada) 
                        : dados.conclusao_personalizada;
                } catch(e) {}
            }
            
            blocos = [];
            
            if (salvo && salvo.blocos && Array.isArray(salvo.blocos)) {
                // Formato novo (array)
                blocos = salvo.blocos.map(b => ({
                    id: b.id,
                    titulo: b.titulo || '',
                    html: b.html || '',
                    excluido: !!b.excluido,
                    extra: !!(b.id && b.id.startsWith('novo-'))
                }));
            } else if (salvo && Object.keys(salvo).length > 0) {
                // Formato antigo (objeto chave-valor)
                Object.entries(TITULOS_FIXOS).forEach(([idB, titulo]) => {
                    blocos.push({
                        id: idB,
                        titulo: titulo,
                        html: salvo[idB] || '',
                        excluido: false,
                        extra: false
                    });
                });
            } else {
                // Extrai do relatório
                await extrairDoRelatorio(id);
            }
            
            renderizar();
        } catch(e) {
            console.error(e);
            alert("Erro ao carregar.");
        }
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
                        blocos.push({
                            id: idB,
                            titulo: titulo,
                            html: el ? el.innerHTML : '',
                            excluido: false,
                            extra: false
                        });
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
            
            // Checkbox excluir
            html += '<label style="display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px; color: #718096; user-select: none; white-space: nowrap;">';
            html += '<input type="checkbox" class="bloco-excluir" data-index="' + index + '" ' + (bloco.excluido ? 'checked' : '') + '>';
            html += 'Excluir do PDF</label>';
            
            // Título (editável se for extra)
            if (bloco.extra) {
                html += '<input type="text" class="bloco-titulo" data-index="' + index + '" value="' + bloco.titulo.replace(/"/g, '&quot;') + '" style="flex: 1; font-weight: bold; font-size: 14px; padding: 5px; border: 1px solid #cbd5e0; border-radius: 4px;">';
                html += '<button class="bloco-remover" data-index="' + index + '" style="background: #dc2626; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px;">✕ Remover</button>';
            } else {
                html += '<span style="flex: 1; font-weight: bold; font-size: 14px; ' + (bloco.excluido ? 'text-decoration: line-through; color: #999;' : '') + '">' + bloco.titulo + '</span>';
            }
            
            html += '</div>';
            
            // Conteúdo
            html += '<div class="bloco-conteudo" contenteditable="' + (bloco.excluido ? 'false' : 'true') + '" data-index="' + index + '" ';
            html += 'style="min-height: 70px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px; background: #fff; line-height: 1.6; font-size: 14px; ' + (bloco.excluido ? 'pointer-events: none; opacity: 0.5;' : '') + '">';
            html += bloco.html;
            html += '</div>';
            
            div.innerHTML = html;
            lista.appendChild(div);
        });
        
        // Listeners
        lista.querySelectorAll('.bloco-excluir').forEach(chk => {
            chk.addEventListener('change', function() {
                const idx = parseInt(this.dataset.index);
                blocos[idx].excluido = this.checked;
                renderizar();
            });
        });
        
        lista.querySelectorAll('.bloco-conteudo').forEach(div => {
            div.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                if (!blocos[idx].excluido) {
                    blocos[idx].html = this.innerHTML;
                }
            });
        });
        
        lista.querySelectorAll('.bloco-titulo').forEach(inp => {
            inp.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                blocos[idx].titulo = this.value;
            });
        });
        
        lista.querySelectorAll('.bloco-remover').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.dataset.index);
                if (confirm('Remover este bloco novo?')) {
                    blocos.splice(idx, 1);
                    renderizar();
                }
            });
        });
    }
    
    btnIncluir.addEventListener('click', function() {
        const numExtras = blocos.filter(b => b.extra).length + 1;
        blocos.push({
            id: 'novo-' + Date.now(),
            titulo: 'Bloco Adicional ' + numExtras,
            html: '<p>Digite aqui o conteúdo do novo bloco...</p>',
            excluido: false,
            extra: true
        });
        renderizar();
        setTimeout(() => lista.scrollTop = lista.scrollHeight, 100);
    });
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        
        // Salva no formato novo
        const payload = { blocos: blocos.map(b => ({
            id: b.id,
            titulo: b.titulo,
            html: b.html,
            excluido: b.excluido
        })) };
        
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: JSON.stringify(payload) })
            });
            const data = await res.json();
            
            if (data.erro) {
                alert("Erro: " + data.mensagem);
            } else {
                alert("Conclusão salva! Agora clique em 'Gerar PDF'.");
                modal.style.display = 'none';
            }
        } catch(e) {
            alert("Erro de conexão.");
        } finally {
            btnSalvar.innerText = "💾 Salvar Conclusão";
            btnSalvar.disabled = false;
        }
    });
});
</script>
"""

c = c.replace('</body>', novo_modal + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c)
print("[OK] Modal atualizado com checkboxes e botao incluir!")


# ==========================================
# 2. RELATORIO - APLICAR EDICOES, EXCLUSOES E EXTRAS
# ==========================================
rel_path = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(rel_path, f"{rel_path}.bak_final_inc_exc_{ts}")
c_rel = open(rel_path, encoding='utf-8').read()

# Remove script antigo
c_rel = re.sub(r'<script id="js-carregar-conclusao-salva">.*?</script>', '', c_rel, flags=re.DOTALL)

novo_js_rel = """
<script id="js-carregar-conclusao-salva">
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const historicoId = urlParams.get('historico_id');
    if (!historicoId) return;
    
    fetch(`/historico_centro_custos/${historicoId}`)
        .then(res => res.json())
        .then(data => {
            const dados = data.dados ? data.dados : data;
            if (!dados.conclusao_personalizada) return;
            
            let salvos;
            try {
                salvos = typeof dados.conclusao_personalizada === 'string' 
                    ? JSON.parse(dados.conclusao_personalizada) 
                    : dados.conclusao_personalizada;
            } catch(e) { return; }
            
            // Se for formato antigo (objeto chave-valor), converte
            if (!salvos.blocos && typeof salvos === 'object') {
                const titulosAntigos = {
                    'conclusao-total': '1. Conclusão sobre o Total Executado',
                    'conclusao-concentracao': '2. Análise de Concentração',
                    'conclusao-alertas': '3. Alertas e Pontos de Atenção',
                    'conclusao-recomendacoes': '4. Recomendações'
                };
                const blocosConvertidos = Object.entries(titulosAntigos).map(([id, titulo]) => ({
                    id: id,
                    titulo: titulo,
                    html: salvos[id] || '',
                    excluido: false
                }));
                salvos = { blocos: blocosConvertidos };
            }
            
            if (!salvos.blocos || !Array.isArray(salvos.blocos)) return;
            
            // Encontra o container (div após o h2 de conclusão)
            const h2 = Array.from(document.querySelectorAll('h2')).find(h => 
                h.innerText.includes('Conclusão e Recomendações')
            );
            if (!h2) return;
            
            const container = h2.nextElementSibling;
            if (!container) return;
            
            // Para cada bloco salvo (fixos ou extras)
            salvos.blocos.forEach(b => {
                if (!b.id) return;
                
                if (b.id.startsWith('novo-')) {
                    // Bloco NOVO: adiciona no final (se não estiver excluido)
                    if (!b.excluido) {
                        const novoCard = document.createElement('div');
                        novoCard.style.cssText = 'background: var(--bg-light); padding: 25px; border-radius: 8px; border-left: 4px solid #3182ce; margin-top: 20px; page-break-inside: avoid;';
                        novoCard.innerHTML = '<h3 style="color: var(--primary); margin-top: 0;">' + (b.titulo || 'Bloco Adicional') + '</h3>' + 
                                            '<div style="font-size: 14px; line-height: 1.6; background: #fff; padding: 10px; border-radius: 4px;">' + (b.html || '') + '</div>';
                        container.appendChild(novoCard);
                    }
                } else {
                    // Bloco ORIGINAL: encontra e aplica
                    const el = document.getElementById(b.id);
                    if (!el) return;
                    
                    // Sobe até achar o card (div que tem background/padding)
                    let card = el.parentElement;
                    for (let i = 0; i < 3 && card; i++) {
                        if (card.style.background && card.style.padding) break;
                        card = card.parentElement;
                    }
                    if (!card) card = el.parentElement;
                    
                    if (b.excluido) {
                        card.style.display = 'none';
                    } else {
                        if (b.html) el.innerHTML = b.html;
                        // Atualiza o título do h3 dentro do card (se mudou)
                        if (b.titulo && card) {
                            const h3 = card.querySelector('h3');
                            if (h3) h3.innerText = b.titulo;
                        }
                    }
                }
            });
            
            window.conclusaoPersonalizada = true;
        }).catch(e => console.log("Erro:", e));
});

const timer = setInterval(() => {
    if (typeof window.preencherConclusao === 'function') {
        const original = window.preencherConclusao;
        window.preencherConclusao = function(d) {
            if (window.conclusaoPersonalizada) return;
            original(d);
        };
        clearInterval(timer);
    }
}, 100);
</script>
"""

c_rel = c_rel.replace('</body>', novo_js_rel + '\n</body>', 1)
open(rel_path, 'w', encoding='utf-8').write(c_rel)
print("[OK] Relatorio atualizado para respeitar exclusoes e blocos extras!")
print()
print("=== INSTRUCOES DE TESTE ===")
print("1. Va na tela de Analise por Centro de Custos e aperte Ctrl+F5")
print("2. Marque um historico e clique em 'Editar Conclusao'")
print("3. Teste: editar texto, marcar 'Excluir do PDF', incluir novo bloco")
print("4. Clique em 'Salvar Conclusao'")
print("5. Gere o PDF e confira o resultado")
