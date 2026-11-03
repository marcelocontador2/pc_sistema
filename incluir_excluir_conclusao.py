import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. MODAL DA TELA PRINCIPAL
# ==========================================
main_path = r"pc_frontend\analise_centro_custos.html"
shutil.copy2(main_path, f"{main_path}.bak_inc_exc_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove o modal antigo inteiro
c_main = re.sub(r'<div id="modal-conclusao".*?</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<div id="modal-conclusao".*?</div>\s*</div>\s*</div>\s*</div>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# Novo modal com suporte a incluir/excluir
novo_modal = """
<div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
    <div style="background: white; padding: 25px; border-radius: 12px; width: 1000px; max-width: 98%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #1a202c;">✏️ Editar Conclusão do Relatório</h3>
            <button id="btn-restaurar-todos" style="background: #718096; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 13px;">↺ Restaurar todos</button>
        </div>
        
        <p style="color: #718096; font-size: 13px; margin: 0 0 15px 0;">Edite, exclua (🗑️) ou inclua (➕) blocos. O PDF refletirá as mudanças.</p>
        
        <div id="lista-blocos" style="overflow-y: auto; flex: 1; padding-right: 5px;">
            <!-- Blocos serão renderizados aqui via JS -->
        </div>
        
        <div style="margin-top: 15px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
            <button id="btn-adicionar-bloco" style="background: #3182ce; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;">➕ Incluir Novo Bloco</button>
        </div>
        
        <div style="margin-top: 15px; display: flex; justify-content: flex-end; gap: 10px;">
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
    const btnAdicionar = document.getElementById('btn-adicionar-bloco');
    const btnRestaurar = document.getElementById('btn-restaurar-todos');
    const listaBlocos = document.getElementById('lista-blocos');
    
    // Estrutura: { blocos: [{id, titulo, html, excluido}], extras: [] }
    let estado = { blocos: [], extras: [] };
    
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
            
            let textoSalvo = null;
            if (dados.conclusao_personalizada) {
                try {
                    textoSalvo = typeof dados.conclusao_personalizada === 'string' 
                        ? JSON.parse(dados.conclusao_personalizada) 
                        : dados.conclusao_personalizada;
                } catch(e) {}
            }
            
            if (textoSalvo && textoSalvo.blocos && Array.isArray(textoSalvo.blocos)) {
                // Novo formato com array de blocos
                estado = textoSalvo;
            } else if (textoSalvo && Object.keys(textoSalvo).length > 0) {
                // Formato antigo (chave-valor) - converte para novo
                const titulos = {
                    'conclusao-total': '1. Conclusão sobre o Total Executado',
                    'conclusao-concentracao': '2. Análise de Concentração',
                    'conclusao-alertas': '3. Alertas e Pontos de Atenção',
                    'conclusao-recomendacoes': '4. Recomendações'
                };
                estado.blocos = Object.entries(titulos).map(([id, titulo]) => ({
                    id: id,
                    titulo: titulo,
                    html: textoSalvo[id] || '',
                    excluido: false
                }));
                estado.extras = [];
            } else {
                // Extrai do relatório
                estado = await extrairDoRelatorio(id);
            }
            
            renderizarBlocos();
            
        } catch(e) {
            console.error("Erro:", e);
            alert("Erro ao carregar os textos.");
            listaBlocos.innerHTML = '<div style="color:red;">Erro ao carregar.</div>';
        }
    });
    
    function extrairDoRelatorio(historicoId) {
        return new Promise((resolve) => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `/relatorio_centro_custos?historico_id=${historicoId}&_t=${Date.now()}`;
            document.body.appendChild(iframe);
            
            setTimeout(() => {
                const resultado = { blocos: [], extras: [] };
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const titulos = {
                        'conclusao-total': '1. Conclusão sobre o Total Executado',
                        'conclusao-concentracao': '2. Análise de Concentração',
                        'conclusao-alertas': '3. Alertas e Pontos de Atenção',
                        'conclusao-recomendacoes': '4. Recomendações'
                    };
                    
                    for (const [id, titulo] of Object.entries(titulos)) {
                        const el = doc.getElementById(id);
                        resultado.blocos.push({
                            id: id,
                            titulo: titulo,
                            html: el ? el.innerHTML : '',
                            excluido: false
                        });
                    }
                    document.body.removeChild(iframe);
                    resolve(resultado);
                } catch(e) {
                    console.error(e);
                    document.body.removeChild(iframe);
                    resolve(resultado);
                }
            }, 4000);
        });
    }
    
    function renderizarBlocos() {
        listaBlocos.innerHTML = '';
        
        estado.blocos.forEach((bloco, index) => {
            const div = document.createElement('div');
            div.className = 'bloco-edicao';
            div.style.cssText = 'border: 1px solid #cbd5e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: ' + (bloco.excluido ? '#fef2f2' : '#fff') + '; opacity: ' + (bloco.excluido ? '0.5' : '1') + ';';
            
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <input type="text" class="bloco-titulo" value="${bloco.titulo}" 
                           style="flex: 1; font-weight: bold; font-size: 15px; padding: 5px; border: 1px solid #e2e8f0; border-radius: 4px; ${bloco.excluido ? 'text-decoration: line-through;' : ''}"
                           data-index="${index}">
                    <button class="btn-excluir-bloco" data-index="${index}" 
                            style="background: ${bloco.excluido ? '#38a169' : '#e53e3e'}; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; margin-left: 10px; font-size: 13px;">
                        ${bloco.excluido ? '↺ Restaurar' : '🗑️ Excluir'}
                    </button>
                </div>
                <div class="bloco-conteudo" contenteditable="true" data-index="${index}"
                     style="min-height: 80px; padding: 10px; border: 1px solid #e2e8f0; border-radius: 4px; background: #f8fafc; line-height: 1.6; font-size: 14px; ${bloco.excluido ? 'pointer-events: none;' : ''}">
                    ${bloco.html}
                </div>
            `;
            
            listaBlocos.appendChild(div);
        });
        
        // Event listeners dos títulos
        listaBlocos.querySelectorAll('.bloco-titulo').forEach(input => {
            input.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                estado.blocos[idx].titulo = this.value;
            });
        });
        
        // Event listeners dos conteúdos
        listaBlocos.querySelectorAll('.bloco-conteudo').forEach(div => {
            div.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                if (!estado.blocos[idx].excluido) {
                    estado.blocos[idx].html = this.innerHTML;
                }
            });
        });
        
        // Event listeners dos botões excluir
        listaBlocos.querySelectorAll('.btn-excluir-bloco').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.dataset.index);
                estado.blocos[idx].excluido = !estado.blocos[idx].excluido;
                renderizarBlocos();
            });
        });
    }
    
    btnAdicionar.addEventListener('click', function() {
        estado.blocos.push({
            id: 'novo-' + Date.now(),
            titulo: 'Novo Bloco',
            html: '<p>Digite aqui o conteúdo...</p>',
            excluido: false
        });
        renderizarBlocos();
        // Rola para o final
        setTimeout(() => listaBlocos.scrollTop = listaBlocos.scrollHeight, 100);
    });
    
    btnRestaurar.addEventListener('click', function() {
        if (confirm("Restaurar todos os blocos excluídos?")) {
            estado.blocos.forEach(b => b.excluido = false);
            renderizarBlocos();
        }
    });
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: JSON.stringify(estado) })
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
print("[OK] Modal com Incluir/Excluir blocos criado!")


# ==========================================
# 2. RELATÓRIO - RENDERIZAR COM EXCLUSÕES E EXTRAS
# ==========================================
rel_path = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(rel_path, f"{rel_path}.bak_inc_exc_{ts}")
c_rel = open(rel_path, encoding='utf-8').read()

# Remove script antigo de carregamento
c_rel = re.sub(r'<script id="js-carregar-conclusao-salva">.*?</script>', '', c_rel, flags=re.DOTALL)

# Novo script que aplica exclusões e adiciona blocos extras
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
            } catch(e) {
                console.log("Formato antigo, ignorando:", e);
                return;
            }
            
            // Novo formato com array
            if (salvos.blocos && Array.isArray(salvos.blocos)) {
                // Encontra a div que contém os blocos (após o h2 de conclusão)
                const h2 = Array.from(document.querySelectorAll('h2')).find(h => 
                    h.innerText.includes('Conclusão e Recomendações')
                );
                if (!h2) return;
                
                const container = h2.nextElementSibling;
                if (!container) return;
                
                // Guarda referências dos blocos originais por ID
                const blocosOriginais = {};
                salvos.blocos.forEach(b => {
                    if (b.id && !b.id.startsWith('novo-')) {
                        const el = document.getElementById(b.id);
                        if (el) {
                            // Encontra a div "card" (pai do elemento com ID)
                            blocosOriginais[b.id] = el.closest('div[style*="background"]') || el.parentElement;
                        }
                    }
                });
                
                // Aplica exclusões (oculta os blocos excluídos)
                salvos.blocos.forEach(b => {
                    if (b.excluido && b.id && !b.id.startsWith('novo-')) {
                        const el = document.getElementById(b.id);
                        if (el) {
                            const card = el.closest('div[style*="background"]') || el.parentElement;
                            if (card) card.style.display = 'none';
                        }
                    }
                });
                
                // Aplica conteúdo editado nos blocos originais
                salvos.blocos.forEach(b => {
                    if (b.id && !b.id.startsWith('novo-') && b.html) {
                        const el = document.getElementById(b.id);
                        if (el) el.innerHTML = b.html;
                    }
                });
                
                // Adiciona blocos extras (novos)
                salvos.blocos.filter(b => b.id && b.id.startsWith('novo-') && !b.excluido).forEach(b => {
                    const novoCard = document.createElement('div');
                    novoCard.style.cssText = 'background: var(--bg-light); padding: 25px; border-radius: 8px; border-left: 4px solid #3182ce; margin-top: 20px; page-break-inside: avoid;';
                    novoCard.innerHTML = '<h3 style="color: var(--primary); margin-top: 0;">' + b.titulo + '</h3>' + 
                                        '<div style="font-size: 14px; line-height: 1.6; background: #fff; padding: 10px; border-radius: 4px;">' + b.html + '</div>';
                    container.appendChild(novoCard);
                });
                
                window.conclusaoPersonalizada = true;
            }
        }).catch(e => console.log("Erro ao carregar conclusão:", e));
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
print("[OK] Relatório atualizado para respeitar exclusões e blocos extras!")
