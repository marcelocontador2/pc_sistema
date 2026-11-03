import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_edicao_direta_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove o textarea antigo que havíamos injetado
c = re.sub(r'<div id="bloco-conclusao".*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# 2. Injeta o novo script de edição (WYSIWYG)
novo_sistema = """
    <!-- BARRA DE FERRAMENTAS FLUTUANTE -->
    <div id="barra-edicao" style="position: fixed; bottom: 30px; right: 30px; display: flex; gap: 10px; z-index: 9999; box-shadow: 0 4px 12px rgba(0,0,0,0.2); border-radius: 8px; background: white; padding: 10px;">
        <button id="btn-editar" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 5px;">✏️ Editar Conclusão</button>
        <button id="btn-salvar" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: none; align-items: center; gap: 5px;">💾 Salvar Relatório</button>
    </div>

    <style>
        /* Estilo para quando estiver no modo de edição */
        .editando-conclusao {
            border: 2px dashed #f59e0b !important;
            padding: 15px !important;
            border-radius: 8px !important;
            background-color: #fffbeb !important;
        }
        @media print {
            #barra-edicao { display: none !important; }
            .editando-conclusao { border: none !important; padding: 0 !important; background: transparent !important; }
        }
    </style>

    <script id="sistema-edicao-direta">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            const btnEditar = document.getElementById('btn-editar');
            const btnSalvar = document.getElementById('btn-salvar');
            
            let areaConclusao = null;

            // Função para achar o container que tem a palavra "Conclusão"
            function encontrarArea() {
                const headers = document.querySelectorAll('h1, h2, h3, h4');
                for (let h of headers) {
                    if (h.innerText.toUpperCase().includes('1. CONCLUSÃO') || h.innerText.toUpperCase().includes('RECOMENDAÇÕES')) {
                        // Pega o container pai que engloba os 4 blocos
                        areaConclusao = h.closest('.page') || h.parentElement.parentElement;
                        return;
                    }
                }
            }

            // 1. Carregar HTML salvo anteriormente
            if (historicoId) {
                fetch(`/historico_centro_custos/${historicoId}`)
                    .then(res => res.json())
                    .then(data => {
                        const dados = data.dados ? data.dados : data;
                        if (dados.conclusao_personalizada) {
                            encontrarArea();
                            if (areaConclusao) {
                                areaConclusao.innerHTML = dados.conclusao_personalizada;
                            }
                        }
                    }).catch(e => console.log("Erro ao carregar:", e));
            }

            // 2. Ativar modo de edição
            btnEditar.addEventListener('click', function() {
                if (!areaConclusao) encontrarArea();
                if (!areaConclusao) { alert("Seção de conclusão não encontrada."); return; }

                areaConclusao.setAttribute('contenteditable', 'true');
                areaConclusao.classList.add('editando-conclusao');
                areaConclusao.focus();
                
                btnEditar.style.display = 'none';
                btnSalvar.style.display = 'flex';
            });

            // 3. Salvar as alterações
            btnSalvar.addEventListener('click', function() {
                if (!historicoId) {
                    alert("Você precisa estar visualizando um histórico para salvar.");
                    return;
                }

                const htmlEditado = areaConclusao.innerHTML;
                btnSalvar.innerText = "Salvando...";
                btnSalvar.disabled = true;

                fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ texto: htmlEditado }) // Salva o HTML ao invés de texto puro
                })
                .then(res => res.json())
                .then(data => {
                    if (data.erro) {
                        alert("Erro: " + data.mensagem);
                    } else {
                        areaConclusao.removeAttribute('contenteditable');
                        areaConclusao.classList.remove('editando-conclusao');
                        btnEditar.style.display = 'flex';
                        btnSalvar.style.display = 'none';
                        btnSalvar.innerText = "💾 Salvar Relatório";
                        btnSalvar.disabled = false;
                    }
                })
                .catch(() => {
                    alert("Erro de conexão.");
                    btnSalvar.innerText = "💾 Salvar Relatório";
                    btnSalvar.disabled = false;
                });
            });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', novo_sistema + '\n</body>', 1)
else:
    c += novo_sistema

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Sistema de edição direta da conclusão (WYSIWYG) injetado!")
