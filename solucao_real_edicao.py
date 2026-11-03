import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. LIMPA O RELATÓRIO (remove botões que não funcionavam)
# ==========================================
rel_path = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(rel_path, f"{rel_path}.bak_clean_{ts}")
c = open(rel_path, encoding='utf-8').read()

# Remove TODAS as tentativas anteriores
c = re.sub(r'<div id="barra-edicao-conclusao".*?</div>\s*', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="painel-edicao-flutuante".*?</div>\s*', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao[^"]*">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="script-edicao[^"]*">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-carregar-conclusao-salva">.*?</script>', '', c, flags=re.DOTALL)
c = c.replace('contenteditable="true"', '')

# Adiciona apenas o script que carrega o JSON salvo (espião)
js_load = """
<script id="js-carregar-conclusao-salva">
    document.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        const historicoId = urlParams.get('historico_id');
        if (!historicoId) return;
        
        const blocos = ['conclusao-total', 'conclusao-concentracao', 'conclusao-alertas', 'conclusao-recomendacoes'];
        
        fetch(`/historico_centro_custos/${historicoId}`)
            .then(res => res.json())
            .then(data => {
                const dados = data.dados ? data.dados : data;
                if (dados.conclusao_personalizada) {
                    try {
                        const htmlSalvo = typeof dados.conclusao_personalizada === 'string' 
                            ? JSON.parse(dados.conclusao_personalizada) 
                            : dados.conclusao_personalizada;
                        
                        blocos.forEach(id => {
                            const el = document.getElementById(id);
                            if (el && htmlSalvo[id]) {
                                el.innerHTML = htmlSalvo[id];
                            }
                        });
                        window.conclusaoPersonalizada = htmlSalvo;
                    } catch(e) {
                        console.log("Aviso: erro ao ler conclusão.", e);
                    }
                }
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
c = c.replace('</body>', js_load + '\n</body>', 1)
open(rel_path, 'w', encoding='utf-8').write(c)
print("[OK] Relatório limpo - apenas carrega a conclusão salva.")


# ==========================================
# 2. ADICIONA BOTÃO NA TELA PRINCIPAL (analise_centro_custos.html)
# ==========================================
main_path = r"pc_frontend\analise_centro_custos.html"
shutil.copy2(main_path, f"{main_path}.bak_modal_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove tentativas anteriores
c_main = re.sub(r'<button[^>]*id="btn-editar-conclusao".*?</button>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<div id="modal-conclusao".*?</div>\s*</div>\s*</div>\s*', '', c_main, flags=re.DOTALL)
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# Adiciona botão ao lado do Gerar PDF
btn_edit = '<button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-left: 10px;">✏️ Editar Conclusão</button>'

match_pdf = re.search(r'(<button[^>]*>Gerar PDF</button>)', c_main, re.IGNORECASE)
if match_pdf:
    c_main = c_main.replace(match_pdf.group(1), match_pdf.group(1) + '\n' + btn_edit, 1)

# Adiciona o modal e a lógica
modal = """
<div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 99999; justify-content: center; align-items: center;">
    <div style="background: white; padding: 25px; border-radius: 12px; width: 900px; max-width: 95%; max-height: 90vh; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #1a202c;">✏️ Editar Conclusão do Relatório</h3>
        <p style="color: #718096; font-size: 14px;">Edite os textos abaixo. Eles serão usados no próximo PDF que você gerar.</p>
        
        <label style="display: block; margin-top: 15px; font-weight: bold;">1. Conclusão sobre o Total Executado</label>
        <textarea id="edit-conclusao-total" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>
        
        <label style="display: block; margin-top: 15px; font-weight: bold;">2. Análise de Concentração</label>
        <textarea id="edit-conclusao-concentracao" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>
        
        <label style="display: block; margin-top: 15px; font-weight: bold;">3. Alertas e Pontos de Atenção</label>
        <textarea id="edit-conclusao-alertas" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>
        
        <label style="display: block; margin-top: 15px; font-weight: bold;">4. Recomendações</label>
        <textarea id="edit-conclusao-recomendacoes" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>
        
        <div style="margin-top: 20px; text-align: right; display: flex; gap: 10px; justify-content: flex-end;">
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
    
    const campos = {
        'conclusao-total': document.getElementById('edit-conclusao-total'),
        'conclusao-concentracao': document.getElementById('edit-conclusao-concentracao'),
        'conclusao-alertas': document.getElementById('edit-conclusao-alertas'),
        'conclusao-recomendacoes': document.getElementById('edit-conclusao-recomendacoes')
    };
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        
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
            
            for (const [chave, campo] of Object.entries(campos)) {
                if (textoSalvo && textoSalvo[chave]) {
                    const temp = document.createElement('div');
                    temp.innerHTML = textoSalvo[chave];
                    campo.value = temp.innerText;
                } else {
                    campo.value = '';
                    campo.placeholder = 'Digite aqui a conclusão...';
                }
            }
        } catch(e) {
            console.error(e);
        }
    });
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        
        const htmlEditado = {};
        for (const [chave, campo] of Object.entries(campos)) {
            const texto = campo.value.trim();
            htmlEditado[chave] = texto.split('\\n').map(p => p.trim()).filter(p => p).map(p => '<p>' + p + '</p>').join('');
        }
        
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: JSON.stringify(htmlEditado) })
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
c_main = c_main.replace('</body>', modal + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c_main)
print("[OK] Botão 'Editar Conclusão' e modal adicionados na TELA PRINCIPAL!")
print("[INFO] Fluxo correto agora: 1) Selecione o histórico 2) Clique 'Editar Conclusão' 3) Salve 4) Clique 'Gerar PDF'")
