import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_edicao_melhorada_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove o script anterior
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# Novo script com a lógica de preservar formatação e não sobrescrever texto vazio
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
    
    // Guarda o HTML original de cada bloco para preservar formatação
    window.htmlOriginal = {};
    // Guarda o texto puro original para comparar
    window.textoOriginal = {};
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        window.htmlOriginal = {};
        window.textoOriginal = {};
        
        for (const campo of Object.values(campos)) {
            campo.value = 'Carregando...';
            campo.disabled = true;
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
                // Já tem conclusão salva anteriormente
                for (const [chave, campo] of Object.entries(campos)) {
                    if (textoSalvo[chave]) {
                        const temp = document.createElement('div');
                        temp.innerHTML = textoSalvo[chave];
                        campo.value = temp.innerText.trim();
                        window.htmlOriginal[chave] = textoSalvo[chave];
                        window.textoOriginal[chave] = temp.innerText.trim();
                    } else {
                        campo.value = '';
                        window.htmlOriginal[chave] = '';
                        window.textoOriginal[chave] = '';
                    }
                    campo.disabled = false;
                }
            } else {
                // Não tem salvo, extrai do relatório
                await extrairDoRelatorio(id);
            }
        } catch(e) {
            console.error("Erro:", e);
            alert("Erro ao carregar os textos. Tente novamente.");
            for (const campo of Object.values(campos)) campo.disabled = false;
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
                            // Guarda o HTML com formatação
                            window.htmlOriginal[chave] = el.innerHTML;
                            // Mostra texto puro no textarea
                            const textoPuro = el.innerText.trim();
                            window.textoOriginal[chave] = textoPuro;
                            campo.value = textoPuro;
                        } else {
                            window.htmlOriginal[chave] = '';
                            window.textoOriginal[chave] = '';
                            campo.value = '';
                        }
                        campo.disabled = false;
                    }
                    document.body.removeChild(iframe);
                    resolve();
                } catch(e) {
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
            const textoDigitado = campo.value.trim();
            const textoOriginal = (window.textoOriginal[chave] || '').trim();
            const htmlOrig = window.htmlOriginal[chave] || '';
            
            if (!textoDigitado) {
                // Campo vazio → preserva o original (não apaga)
                htmlEditado[chave] = htmlOrig;
            } else if (textoDigitado === textoOriginal) {
                // Texto não mudou → preserva o HTML original (mantém formatação)
                htmlEditado[chave] = htmlOrig;
            } else {
                // Texto mudou → gera novo HTML, só com o que foi digitado
                htmlEditado[chave] = textoDigitado
                    .split('\\n')
                    .map(p => p.trim())
                    .filter(p => p)
                    .map(p => '<p>' + p + '</p>')
                    .join('');
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
print("[OK] Edição melhorada! Agora preserva formatação e não sobrescreve campos vazios.")
