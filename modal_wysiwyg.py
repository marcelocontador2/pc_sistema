import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_wysiwyg_modal_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# 1. Substitui os <textarea> por <div contenteditable>
c_main = c_main.replace(
    '<textarea id="edit-conclusao-total" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>',
    '<div id="edit-conclusao-total" contenteditable="true" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>'
)
c_main = c_main.replace(
    '<textarea id="edit-conclusao-concentracao" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>',
    '<div id="edit-conclusao-concentracao" contenteditable="true" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>'
)
c_main = c_main.replace(
    '<textarea id="edit-conclusao-alertas" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>',
    '<div id="edit-conclusao-alertas" contenteditable="true" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>'
)
c_main = c_main.replace(
    '<textarea id="edit-conclusao-recomendacoes" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px;"></textarea>',
    '<div id="edit-conclusao-recomendacoes" contenteditable="true" style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: inherit; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>'
)

# 2. Remove o script antigo do modal
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# 3. Novo script com lógica de contenteditable
novo_js = """
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
    
    window.htmlOriginal = {};
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        window.htmlOriginal = {};
        
        // Mostra "carregando"
        for (const campo of Object.values(campos)) {
            campo.innerHTML = '<em style="color:#999;">Carregando...</em>';
        }
        
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
            
            if (textoSalvo && Object.keys(textoSalvo).length > 0) {
                // Já tem conclusão salva
                for (const [chave, campo] of Object.entries(campos)) {
                    if (textoSalvo[chave]) {
                        campo.innerHTML = textoSalvo[chave];
                        window.htmlOriginal[chave] = textoSalvo[chave];
                    } else {
                        campo.innerHTML = '';
                        window.htmlOriginal[chave] = '';
                    }
                }
            } else {
                // Extrai do relatório
                await extrairDoRelatorio(id);
            }
        } catch(e) {
            console.error("Erro:", e);
            alert("Erro ao carregar os textos. Tente novamente.");
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
                    for (const [chave, campo] of Object.entries(campos)) {
                        const el = doc.getElementById(chave);
                        if (el) {
                            // Copia o HTML com formatação (negritos, cores, parágrafos)
                            campo.innerHTML = el.innerHTML;
                            window.htmlOriginal[chave] = el.innerHTML;
                        } else {
                            campo.innerHTML = '';
                            window.htmlOriginal[chave] = '';
                        }
                    }
                    document.body.removeChild(iframe);
                    resolve();
                } catch(e) {
                    console.error(e);
                    document.body.removeChild(iframe);
                    resolve();
                }
            }, 4000);
        });
    }
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        const htmlEditado = {};
        
        for (const [chave, campo] of Object.entries(campos)) {
            const htmlAtual = campo.innerHTML.trim();
            const htmlOriginal = (window.htmlOriginal[chave] || '').trim();
            const textoAtual = campo.innerText.trim();
            
            if (!textoAtual) {
                // Vazio → preserva original
                htmlEditado[chave] = htmlOriginal;
            } else if (htmlAtual === htmlOriginal) {
                // Não mudou → preserva original (com formatação)
                htmlEditado[chave] = htmlOriginal;
            } else {
                // Mudou → salva o HTML novo (mantendo formatação que o usuário fez)
                htmlEditado[chave] = htmlAtual;
            }
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

c_main = c_main.replace('</body>', novo_js + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c_main)
print("[OK] Modal agora usa contenteditable - mostra o HTML com formatação real!")
