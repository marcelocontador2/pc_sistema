import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_carregar_{ts}")
c_main = open(main_path, encoding='utf-8').read()

# Remove o script do modal anterior (mas mantém o modal HTML)
c_main = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c_main, flags=re.DOTALL)

# Cria o novo script que carrega os textos reais do relatório via iframe
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
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        
        // Preenche com "Carregando..." enquanto busca
        for (const campo of Object.values(campos)) {
            campo.value = 'Carregando texto do relatório...';
            campo.disabled = true;
        }
        
        try {
            // 1. Verifica se já existe uma conclusão salva
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
            
            // 2. Se já tem salvo, usa ele. Se não, extrai do relatório real via iframe.
            if (textoSalvo && Object.keys(textoSalvo).length > 0) {
                for (const [chave, campo] of Object.entries(campos)) {
                    if (textoSalvo[chave]) {
                        const temp = document.createElement('div');
                        temp.innerHTML = textoSalvo[chave];
                        campo.value = temp.innerText;
                    }
                    campo.disabled = false;
                }
            } else {
                // Extrai do relatório em iframe oculto
                await extrairDoRelatorio(id);
            }
        } catch(e) {
            console.error("Erro:", e);
            alert("Erro ao carregar os textos. Tente novamente.");
        } finally {
            for (const campo of Object.values(campos)) {
                campo.disabled = false;
            }
        }
    });

    function extrairDoRelatorio(historicoId) {
        return new Promise((resolve, reject) => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `/relatorio_centro_custos?historico_id=${historicoId}&_t=${Date.now()}`;
            document.body.appendChild(iframe);
            
            // Espera o iframe carregar e o JS do relatório rodar (4 segundos de margem)
            setTimeout(() => {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    for (const [chave, campo] of Object.entries(campos)) {
                        const el = doc.getElementById(chave);
                        if (el) {
                            campo.value = el.innerText.trim();
                        } else {
                            campo.value = '';
                        }
                    }
                    document.body.removeChild(iframe);
                    resolve();
                } catch(e) {
                    document.body.removeChild(iframe);
                    reject(e);
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
            const texto = campo.value.trim();
            htmlEditado[chave] = texto
                .split('\\n')
                .map(p => p.trim())
                .filter(p => p)
                .map(p => '<p>' + p + '</p>')
                .join('');
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
print("[OK] Modal agora extrai os textos reais do relatório!")
print("[INFO] Se já houver conclusão salva, mostra a salva. Se não, mostra a gerada automaticamente.")
