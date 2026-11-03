import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_edicao_tela_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove scripts de edição anteriores para não dar conflito
c = re.sub(r'<div id="barra-edicao".*?</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# Adiciona o CSS para os botões e para esconder na impressão
css_edit = """
    <style>
        /* Botões de Edição */
        .edit-toolbar {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            margin-top: 20px;
        }
        .btn-edit {
            background: #f59e0b; color: white; border: none; padding: 10px 20px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;
            display: flex; align-items: center; gap: 5px;
        }
        .btn-save {
            background: #38a169; color: white; border: none; padding: 10px 20px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;
            display: none; align-items: center; gap: 5px;
        }
        .btn-save:hover, .btn-edit:hover { opacity: 0.9; }
        
        /* Destaque da área editável */
        .editando {
            outline: 3px dashed #f59e0b;
            outline-offset: 5px;
            background-color: #fffbeb !important;
        }

        /* REGRAS DE IMPRESSÃO: Esconde os botões e o destaque no PDF */
        @media print {
            .edit-toolbar { display: none !important; }
            .editando { outline: none !important; background-color: transparent !important; }
        }
    </style>
"""

if '</head>' in c:
    c = c.replace('</head>', css_edit + '\n</head>', 1)

# Adiciona o Script de Edição
script_edit = """
    <script id="sistema-edicao-tela">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            if (!historicoId) return;

            // 1. Achar a área de conclusão
            let areaConclusao = null;
            const headers = document.querySelectorAll('h1, h2, h3, h4');
            for (let h of headers) {
                if (h.innerText.toUpperCase().includes('CONCLUSÃO E RECOMENDAÇÕES')) {
                    areaConclusao = h.parentElement;
                    break;
                }
            }

            if (!areaConclusao) return;

            // 2. Criar a Barra de Botões
            const toolbar = document.createElement('div');
            toolbar.className = 'edit-toolbar';
            toolbar.innerHTML = `
                <button id="btn-edit-conclusao" class="btn-edit">✏️ Editar Conclusão</button>
                <button id="btn-save-conclusao" class="btn-save">💾 Salvar Relatório</button>
            `;
            // Insere os botões logo antes do título da conclusão
            areaConclusao.insertBefore(toolbar, areaConclusao.firstChild);

            const btnEdit = document.getElementById('btn-edit-conclusao');
            const btnSave = document.getElementById('btn-save-conclusao');

            // 3. Carregar texto salvo anteriormente (se houver)
            fetch(`/historico_centro_custos/${historicoId}`)
                .then(res => res.json())
                .then(data => {
                    const dados = data.dados ? data.dados : data;
                    if (dados.conclusao_personalizada) {
                        areaConclusao.innerHTML = dados.conclusao_personalizada;
                        areaConclusao.insertBefore(toolbar, areaConclusao.firstChild); // Restaura a barra
                    }
                }).catch(e => console.log("Erro ao buscar:", e));

            // 4. Ação do botão Editar
            btnEdit.addEventListener('click', function() {
                areaConclusao.setAttribute('contenteditable', 'true');
                areaConclusao.classList.add('editando');
                btnEdit.style.display = 'none';
                btnSave.style.display = 'flex';
                areaConclusao.focus();
            });

            // 5. Ação do botão Salvar
            btnSave.addEventListener('click', function() {
                const htmlEditado = areaConclusao.innerHTML;
                btnSave.innerText = "Salvando...";
                btnSave.disabled = true;

                fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ texto: htmlEditado })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.erro) alert("Erro: " + data.mensagem);
                    else {
                        areaConclusao.removeAttribute('contenteditable');
                        areaConclusao.classList.remove('editando');
                        btnEdit.style.display = 'flex';
                        btnSave.style.display = 'none';
                        btnSave.innerText = "💾 Salvar Relatório";
                        btnSave.disabled = false;
                        alert("Conclusão salva com sucesso! O PDF usará este texto.");
                    }
                })
                .catch(() => {
                    alert("Erro de conexão.");
                    btnSave.innerText = "💾 Salvar Relatório";
                    btnSave.disabled = false;
                });
            });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_edit + '\n</body>', 1)
else:
    c += script_edit

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botões e edição injetados diretamente na tela do relatório!")
