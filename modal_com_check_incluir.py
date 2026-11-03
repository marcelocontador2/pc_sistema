import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_check_inc_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove modal/script anteriores
c_main = re.sub(r'<div id="modal-conclusao".*?</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# Novo modal com checkboxes e botão de incluir
novo_modal = """
<div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
    <div style="background: white; padding: 25px; border-radius: 12px; width: 1000px; max-width: 98%; max-height: 92vh; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        
        <h3 style="margin: 0 0 10px 0; color: #1a202c;">✏️ Editar Conclusão do Relatório</h3>
        <p style="color: #718096; font-size: 13px; margin: 0 0 15px 0;">Edite os textos, marque a caixinha para excluir do PDF, ou inclua novos blocos.</p>
        
        <div id="lista-blocos" style="overflow-y: auto; flex: 1; padding-right: 5px;">
            <!-- Blocos fixos + extras serão renderizados aqui -->
        </div>
        
        <div style="margin-top: 10px; padding: 10px 0; border-top: 1px solid #e2e8f0;">
            <button id="btn-modal-incluir" style="background: #3182ce; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;">➕ Incluir Novo Bloco</button>
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
    const listaBlocos = document.getElementById('lista-blocos');
    
    // Estado: blocos fixos + extras
    // Cada bloco: {id, titulo, html, excluido, ehExtra}
    let blocos = [];
    let htmlOriginal = {};
    
    const TITULOS_FIXOS = {
        'conclusao-total': '1. Conclusão sobre o Total Executado',
        'conclusao-concentracao': '2. Análise de Concentração',
        'conclusao-alertas': '3. Alertas e Pontos de Atenção',
        'conclusao-recomendacoes': '4. Recomendações'
    };
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        listaBlocos.innerHTML = '<div style="text-align:center; padding:40px; color:#999;">Carregando textos do relatório...</div>';
        
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
            htmlOriginal = {};
            
            // Verifica formato de salvamento
            if (salvo && salvo.blocos && Array.isArray(salvo.blocos)) {
                // Formato novo (com blocos array) - já salvo anteriormente
                blocos = salvo.blocos.map(b => ({
                    id: b.id,
                    titulo: b.titulo || '',
                    html: b.html || '',
                    excluido: !!b.excluido,
                    ehExtra: b.id && b.id.startsWith('novo-')
                }));
            } else if (salvo && !salvo.blocos) {
                // Formato antigo (chave-valor) - já salvo
                Object.entries(TITULOS_FIXOS).forEach(([idB, titulo]) => {
                    blocos.push({
                        id: idB,
                        titulo: titulo,
                        html: salvo[idB] || '',
                        excluido: false,
                        ehExtra: false
                    });
                });
            } else {
                // Extrai do relatório
                await extrairDoRelatorio(id);
            }
            
            // Salva o original para comparação
            blocos.forEach(b => {
                htmlOriginal[b.id] = b.html;
            });
            
            renderizar();
            
        } catch(e) {
            console.error("Erro:", e);
            alert("Erro ao carregar os textos.");
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
                            ehExtra: false
                        });
                    });
                } catch(e) {
                    console.error(e);
                }
                document.body.removeChild(iframe);
                resolve();
            }, 4000);
        });
    }
    
    function renderizar() {
        listaBlocos.innerHTML = '';
        
        blocos.forEach((bloco, index) => {
            const container = document.createElement('div');
            container.style.cssText = 'margin-bottom: 15px; padding: 12px; border: 1px solid ' + (bloco.excluido ? '#fca5a5' : '#e2e8f0') + '; border-radius: 8px; background: ' + (bloco.excluido ? '#fef2f2' : '#f8fafc') + ';';
            
            // Título (editável se for extra, fixo se for padrão)
            const tituloHtml = bloco.ehExtra 
                ? '<input type="text" class="bloco-titulo" data-index="' + index + '" value="' + bloco.titulo.replace(/"/g, '&quot;') + '" style="flex: 1; font-weight: bold; font-size: 14px; padding: 5px; border: 1px solid #cbd5e0; border-radius: 4px;">'
                : '<span class="bloco-titulo-fixo" style="flex: 1; font-weight: bold; font-size: 14px; ' + (bloco.excluido ? 'text-decoration: line-through; color: #999;' : '') + '">' + bloco.titulo + '</span>';
            
            // Checkbox + título + botão remover (se extra)
            const btnRemoverExtra = bloco.ehExtra 
                ? '<button class="btn-remover-extra" data-index="' + index + '" style="background: #dc2626; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; margin-left: 5px;">✕ Remover</button>' 
                : '';
            
            container.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px; color: #718096; user-select: none;">
                        <input type="checkbox" class="bloco-excluir" data-index="${index}" ${bloco.excluido ? 'checked' : ''} style="cursor: pointer;">
                        Excluir do PDF
                    </label>
                    ${tituloHtml}
                    ${btnRemoverExtra}
                </div>
                <div class="bloco-conteudo" contenteditable="true" data-index="${index}" 
                     style="min-height: 70px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px; background: #fff; line-height: 1.6; font-size: 14px; ${bloco.excluido ? 'pointer-events: none; opacity: 0.5;' : ''}">
                    ${bloco.html}
                </div>
            `;
            
            listaBlocos.appendChild(container);
        });
        
        // Event listeners
        listaBlocos.querySelectorAll('.bloco-excluir').forEach(chk => {
            chk.addEventListener('change', function() {
                const idx = parseInt(this.dataset.index);
                blocos[idx].excluido = this.checked;
                renderizar();
            });
        });
        
        listaBlocos.querySelectorAll('.bloco-conteudo').forEach(div => {
            div.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                if (!blocos[idx].excluido) {
                    blocos[idx].html = this.innerHTML;
                }
            });
        });
        
        listaBlocos.querySelectorAll('.bloco-titulo').forEach(inp => {
            inp.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                blocos[idx].titulo = this.value;
            });
        });
        
        listaBlocos.querySelectorAll('.btn-remover-extra').forEach(btn => {
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
        const numExtras = blocos.filter(b => b.ehExtra).length + 1;
        blocos.push({
            id: 'novo-' + Date.now(),
            titulo: 'Bloco Adicional ' + numExtras,
            html: '<p>Digite aqui o conteúdo do novo bloco...</p>',
            excluido: false,
            ehExtra: true
        });
        renderizar();
        // Rola para o final
        setTimeout(() => listaBlocos.scrollTop = listaBlocos.scrollHeight, 100);
    });
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        
        // Salva no formato novo (com blocos array)
        const payload = { blocos: blocos };
        
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
                alert("Conclusão salva com sucesso! Agora clique em 'Gerar PDF' para ver o resultado.");
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

c_main = c_main.replace('</body>', novo_modal + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c_main)
print("[OK] Modal atualizado com checkboxes e botao de incluir!")


# ==========================================
# RELATÓRIO - APLICAR EXCLUSÕES E EXTRAS
# ==========================================
rel_path = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(rel_path, f"{rel_path}.bak_check_inc_{ts}")
c_rel = open(rel_path, encoding='utf-8').read()

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
            
            if (!salvos.blocos || !Array.isArray(salvos.blocos)) return;
            
            const h2 = Array.from(document.querySelectorAll('h2')).find(h => 
                h.innerText.includes('Conclusão e Recomendações')
            );
            if (!h2) return;
            
            const container = h2.nextElementSibling;
            if (!container) return;
            
            // Aplica edicoes, exclusoes e extras
            salvos.blocos.forEach(b => {
                if (!b.id || b.id.startsWith('novo-')) return;
                
                const el = document.getElementById(b.id);
                if (!el) return;
                
                const card = el.closest('div[style*="padding: 25px"]') || 
                             el.closest('div[style*="background"]') || 
                             el.parentElement;
                
                if (b.excluido) {
                    if (card) card.style.display = 'none';
                } else if (b.html) {
                    el.innerHTML = b.html;
                }
            });
            
            // Adiciona extras no final
            salvos.blocos.filter(b => b.id && b.id.startsWith('novo-') && !b.excluido).forEach(b => {
                const novoCard = document.createElement('div');
                novoCard.style.cssText = 'background: var(--bg-light); padding: 25px; border-radius: 8px; border-left: 4px solid #3182ce; margin-top: 20px; page-break-inside: avoid;';
                novoCard.innerHTML = '<h3 style="color: var(--primary); margin-top: 0;">' + b.titulo + '</h3>' + 
                                    '<div style="font-size: 14px; line-height: 1.6; background: #fff; padding: 10px; border-radius: 4px;">' + b.html + '</div>';
                container.appendChild(novoCard);
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
print("[OK] Relatorio atualizado para aplicar exclusoes e extras!")
