import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_definitivo_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa QUALQUER script ou div de edição anterior
c = re.sub(r'<script id="js-edicao-final">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-direta-wysiwyg">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-tela">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="barra-edicao-conclusao".*?</div>', '', c, flags=re.DOTALL)

# 2. Adiciona o CSS (esconde botões no PDF e limpa caracteres estranhos)
css = """
    <style>
        /* Remove ícones e caracteres estranhos no PDF */
        i, .fa, .fas, .far, .fal, .fad, .material-icons, [class^="icon-"], [class*=" icon-"] {
            display: none !important;
        }
        
        /* Estilo da barra de edição */
        #toolbar-conclusao {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            margin-top: 20px;
            padding: 10px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        /* Borda de destaque quando estiver editando */
        .editando-ativo {
            outline: 3px dashed #f59e0b !important;
            outline-offset: 3px;
            background-color: #fffbeb !important;
            padding: 10px !important;
            border-radius: 6px !important;
        }

        /* Regra de impressão: esconde a barra e a borda, deixa só o texto */
        @media print {
            #toolbar-conclusao { display: none !important; }
            .editando-ativo { outline: none !important; background-color: transparent !important; padding: 0 !important; }
        }
    </style>
"""
if '</head>' in c:
    c = c.replace('</head>', css + '\n</head>', 1)

# 3. Adiciona a lógica JS que envelopa a conclusão
js = """
    <script id="script-edicao-definitivo">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');

            // A. Encontrar o título "Conclusão e Recomendações"
            const titles = document.querySelectorAll('h1, h2, h3');
            let tituloConclusao = null;
            for (let t of titles) {
                if (t.innerText.toUpperCase().includes('CONCLUSÃO E RECOMENDAÇÕES') || t.innerText.toUpperCase().includes('CONCLUSÃO')) {
                    tituloConclusao = t;
                    break;
                }
            }

            if (!tituloConclusao) {
                console.log("Aviso: Título de conclusão não encontrado.");
                return;
            }

            // B. Criar uma "Capa" (wrapper) para os elementos após o título
            const wrapper = document.createElement('div');
            wrapper.id = 'conteudo-conclusao';
            
            let proximo = tituloConclusao.nextElementSibling;
            while (proximo) {
                let temp = proximo.nextElementSibling;
                wrapper.appendChild(proximo);
                proximo = temp;
            }
            tituloConclusao.parentNode.insertBefore(wrapper, tituloConclusao.nextSibling);

            // C. Injetar os botões logo após o título
            const toolbar = document.createElement('div');
            toolbar.id = 'toolbar-conclusao';
            toolbar.innerHTML = `
                <button id="btn-edit" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;">✏️ Editar Conclusão</button>
                <button id="btn-save" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: none; font-size: 14px;">💾 Salvar Relatório</button>
                <span id="msg-save" style="display: none; color: #38a169; font-weight: bold; align-items: center;">✓ Salvo com sucesso!</span>
            `;
            tituloConclusao.parentNode.insertBefore(toolbar, wrapper);

            const btnEdit = document.getElementById('btn-edit');
            const btnSave = document.getElementById('btn-save');
            const msgSave = document.getElementById('msg-save');

            // D. Carregar dados salvos (se existirem)
            if (historicoId) {
                fetch(`/historico_centro_custos/${historicoId}`)
                    .then(res => res.json())
                    .then(data => {
                        const dados = data.dados ? data.dados : data;
                        if (dados.conclusao_personalizada) {
                            // Substitui o conteúdo pelo HTML salvo
                            wrapper.innerHTML = dados.conclusao_personalizada;
                            // Marca globalmente para a função automática não sobrescrever
                            window.conclusaoJaCarregada = true;
                        }
                    }).catch(e => console.log("Erro ao carregar histórico:", e));
            }

            // E. Ação do Botão Editar
            btnEdit.addEventListener('click', function() {
                wrapper.setAttribute('contenteditable', 'true');
                wrapper.classList.add('editando-ativo');
                btnEdit.style.display = 'none';
                btnSave.style.display = 'block';
                msgSave.style.display = 'none';
                wrapper.focus();
            });

            // F. Ação do Botão Salvar
            btnSave.addEventListener('click', function() {
                if (!historicoId) {
                    alert("Você precisa estar visualizando um histórico para salvar.");
                    return;
                }

                const htmlEditado = wrapper.innerHTML;
                btnSave.innerText = "Salvando...";
                btnSave.disabled = true;

                fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ texto: htmlEditado })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.erro) {
                        alert("Erro: " + data.mensagem);
                    } else {
                        wrapper.removeAttribute('contenteditable');
                        wrapper.classList.remove('editando-ativo');
                        btnEdit.style.display = 'block';
                        btnSave.style.display = 'none';
                        btnSave.innerText = "💾 Salvar Relatório";
                        btnSave.disabled = false;
                        
                        msgSave.style.display = 'flex';
                        setTimeout(() => msgSave.style.display = 'none', 3000);
                        
                        window.conclusaoJaCarregada = true;
                    }
                })
                .catch(() => alert("Erro de conexão ao salvar."));
            });
        });

        // G. Bloquear a sobrescrita automática
        const timer = setInterval(() => {
            if (typeof window.preencherConclusao === 'function') {
                const original = window.preencherConclusao;
                window.preencherConclusao = function(d) {
                    if (window.conclusaoJaCarregada) return; // Se já tem texto editado, bloqueia
                    original(d);
                };
                clearInterval(timer);
            }
        }, 100);
    </script>
"""
if '</body>' in c:
    c = c.replace('</body>', js + '\n</body>', 1)
else:
    c += js

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Estrutura WYSIWYG blindada injetada com sucesso!")
