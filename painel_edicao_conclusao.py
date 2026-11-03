import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_painel_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove modal e scripts antigos
c_main = re.sub(r'<div id="modal-conclusao".*?</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<button[^>]*id="btn-editar-conclusao".*?</button>\s*', '', c_main, flags=re.DOTALL)

# Adiciona o painel de conclusão ANTES do </body>
painel = """
<!-- PAINEL DE CONCLUSÃO EDITÁVEL -->
<div id="painel-conclusao" style="position: fixed; right: 20px; top: 120px; width: 420px; max-height: calc(100vh - 140px); background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; z-index: 9999;">
    
    <div style="padding: 15px 20px; background: #0a1c3a; color: white; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin: 0; font-size: 16px;">✏️ Editar Conclusões</h3>
        <button id="btn-toggle-painel" style="background: transparent; color: white; border: none; font-size: 20px; cursor: pointer;">−</button>
    </div>
    
    <div id="painel-conteudo" style="overflow-y: auto; flex: 1; padding: 15px;">
        <div style="text-align: center; padding: 20px; color: #999; font-size: 13px;">
            Selecione um item no Histórico Salvo para carregar as conclusões.
        </div>
    </div>
    
    <div style="padding: 12px; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; justify-content: space-between;">
        <button id="btn-painel-adicionar" style="background: #3182ce; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; flex: 1;">➕ Incluir Bloco</button>
        <button id="btn-painel-salvar" style="background: #38a169; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; flex: 1;">💾 Salvar</button>
    </div>
</div>

<script id="js-painel-conclusao">
document.addEventListener('DOMContentLoaded', function() {
    const painel = document.getElementById('painel-conclusao');
    const conteudo = document.getElementById('painel-conteudo');
    const btnAdicionar = document.getElementById('btn-painel-adicionar');
    const btnSalvar = document.getElementById('btn-painel-salvar');
    const btnToggle = document.getElementById('btn-toggle-painel');
    let estado = { blocos: [] };
    let historicoAtual = null;
    
    btnToggle.addEventListener('click', function() {
        if (conteudo.style.display === 'none') {
            conteudo.style.display = 'block';
            btnToggle.innerText = '−';
        } else {
            conteudo.style.display = 'none';
            btnToggle.innerText = '+';
        }
    });
    
    // Monitora quando o usuário marca um histórico
    document.addEventListener('change', async function(e) {
        if (e.target.classList.contains('check-historico') && e.target.checked) {
            const id = e.target.value;
            historicoAtual = id;
            await carregarConclusoes(id);
        }
    });
    
    async function carregarConclusoes(id) {
        conteudo.innerHTML = '<div style="text-align: center; padding: 20px; color: #999; font-size: 13px;">Carregando textos do relatório...</div>';
        
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
            
            if (textoSalvo && textoSalvo.blocos && Array.isArray(textoSalvo.blocos) && textoSalvo.blocos.length > 0) {
                estado = textoSalvo;
                renderizar();
            } else {
                await extrairDoRelatorio(id);
                renderizar();
            }
        } catch(e) {
            console.error(e);
            conteudo.innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Erro ao carregar.</div>';
        }
    }
    
    function extrairDoRelatorio(id) {
        return new Promise((resolve) => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `/relatorio_centro_custos?historico_id=${id}&_t=${Date.now()}`;
            document.body.appendChild(iframe);
            
            setTimeout(() => {
                estado = { blocos: [] };
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const titulos = {
                        'conclusao-total': '1. Conclusão sobre o Total Executado',
                        'conclusao-concentracao': '2. Análise de Concentração',
                        'conclusao-alertas': '3. Alertas e Pontos de Atenção',
                        'conclusao-recomendacoes': '4. Recomendações'
                    };
                    
                    for (const [idB, titulo] of Object.entries(titulos)) {
                        const el = doc.getElementById(idB);
                        estado.blocos.push({
                            id: idB,
                            titulo: titulo,
                            html: el ? el.innerHTML : '',
                            excluido: false
                        });
                    }
                } catch(e) {
                    console.error(e);
                }
                document.body.removeChild(iframe);
                resolve();
            }, 4000);
        });
    }
    
    function renderizar() {
        conteudo.innerHTML = '';
        
        if (estado.blocos.length === 0) {
            conteudo.innerHTML = '<div style="text-align: center; padding: 20px; color: #999; font-size: 13px;">Nenhum bloco. Clique em "Incluir Bloco" abaixo.</div>';
            return;
        }
        
        estado.blocos.forEach((bloco, index) => {
            const div = document.createElement('div');
            div.style.cssText = 'border: 1px solid #cbd5e0; border-radius: 8px; padding: 10px; margin-bottom: 10px; background: ' + (bloco.excluido ? '#fef2f2' : '#fff') + '; opacity: ' + (bloco.excluido ? '0.6' : '1') + ';';
            
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 5px;">
                    <input type="text" class="painel-titulo" value="${bloco.titulo.replace(/"/g, '&quot;')}" data-index="${index}"
                           style="flex: 1; font-weight: bold; font-size: 12px; padding: 5px; border: 1px solid #e2e8f0; border-radius: 3px; ${bloco.excluido ? 'text-decoration: line-through;' : ''}">
                    <button class="painel-excluir" data-index="${index}" 
                            style="background: ${bloco.excluido ? '#38a169' : '#e53e3e'}; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; font-size: 11px;">
                        ${bloco.excluido ? '↺' : '🗑️'}
                    </button>
                </div>
                <div class="painel-conteudo-bloco" contenteditable="true" data-index="${index}"
                     style="min-height: 60px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 3px; background: #f8fafc; line-height: 1.5; font-size: 12px; ${bloco.excluido ? 'pointer-events: none;' : ''}">
                    ${bloco.html}
                </div>
            `;
            
            conteudo.appendChild(div);
        });
        
        // Listeners
        conteudo.querySelectorAll('.painel-titulo').forEach(inp => {
            inp.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                estado.blocos[idx].titulo = this.value;
            });
        });
        
        conteudo.querySelectorAll('.painel-conteudo-bloco').forEach(div => {
            div.addEventListener('input', function() {
                const idx = parseInt(this.dataset.index);
                if (!estado.blocos[idx].excluido) {
                    estado.blocos[idx].html = this.innerHTML;
                }
            });
        });
        
        conteudo.querySelectorAll('.painel-excluir').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.dataset.index);
                estado.blocos[idx].excluido = !estado.blocos[idx].excluido;
                renderizar();
            });
        });
    }
    
    btnAdicionar.addEventListener('click', function() {
        if (!historicoAtual) {
            alert("Selecione um histórico primeiro.");
            return;
        }
        estado.blocos.push({
            id: 'novo-' + Date.now(),
            titulo: 'Novo Bloco ' + (estado.blocos.filter(b => b.id.startsWith('novo-')).length + 1),
            html: '<p>Digite aqui o conteúdo...</p>',
            excluido: false
        });
        renderizar();
    });
    
    btnSalvar.addEventListener('click', async function() {
        if (!historicoAtual) {
            alert("Selecione um histórico primeiro.");
            return;
        }
        
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${historicoAtual}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: JSON.stringify(estado) })
            });
            const data = await res.json();
            
            if (data.erro) {
                alert("Erro: " + data.mensagem);
            } else {
                alert("Conclusão salva com sucesso! Agora clique em 'Gerar PDF'.");
            }
        } catch(e) {
            alert("Erro de conexão.");
        } finally {
            btnSalvar.innerText = "💾 Salvar";
            btnSalvar.disabled = false;
        }
    });
});
</script>
"""

c_main = c_main.replace('</body>', painel + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c_main)
print("[OK] Painel de edição de conclusões adicionado na TELA PRINCIPAL!")
print("[INFO] O painel fica no canto direito da tela de Análise por Centro de Custos")
