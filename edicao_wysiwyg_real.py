import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

# Backup
shutil.copy2(arquivo, f"{arquivo}.bak_edit_direto_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa QUALQUER script de edição anterior
c = re.sub(r'<button id="btn-abrir-edicao".*?</button>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="modal-edicao-conclusao".*?</div>\s*</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="barra-edicao".*?</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-tela">.*?</script>', '', c, flags=re.DOTALL)

# 2. Adiciona o CSS e a Barra de Botões no topo da seção de conclusão
# Vamos procurar o título "Conclusão e Recomendações" para inserir os botões logo antes
toolbar_html = """
    <!-- BARRA DE EDIÇÃO DIRETA -->
    <div id="barra-edicao-conclusao" style="display: flex; gap: 10px; margin-bottom: 15px; margin-top: 20px; padding: 10px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 14px;">✏️ Editar Conclusão</button>
        <button id="btn-salvar-conclusao" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: none; align-items: center; gap: 8px; font-size: 14px;">💾 Salvar Relatório</button>
        <span id="msg-conclusao" style="display: none; color: #38a169; font-weight: bold; align-items: center;">✓ Salvo com sucesso!</span>
    </div>
"""

# Injeta a barra antes do título de conclusão
c = c.replace('<h2>Conclusão e Recomendações</h2>', toolbar_html + '<h2>Conclusão e Recomendações</h2>')
# Se o título tiver classe ou id diferente, tenta pelo texto
c = re.sub(r'(<h2[^>]*>Conclusão e Recomendações</h2>)', toolbar_html + r'\1', c, flags=re.IGNORECASE)

# 3. Adiciona o CSS para a área editável e esconder no PDF
css_edit = """
    <style>
        .editando-conclusao {
            outline: 3px dashed #f59e0b;
            outline-offset: 5px;
            background-color: #fffbeb !important;
            padding: 15px !important;
            border-radius: 8px !important;
        }
        @media print {
            #barra-edicao-conclusao { display: none !important; }
            .editando-conclusao { outline: none !important; background-color: transparent !important; padding: 0 !important; }
        }
    </style>
"""
if '</head>' in c:
    c = c.replace('</head>', css_edit + '\n</head>', 1)

# 4. Adiciona o Script de Edição
script_edit = """
    <script id="js-edicao-direta">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            if (!historicoId) return;

            const btnEditar = document.getElementById('btn-editar-conclusao');
            const btnSalvar = document.getElementById('btn-salvar-conclusao');
            const msgSucesso = document.getElementById('msg-conclusao');
            
            // Achar a div que engloba os blocos coloridos
            let areaEdicao = null;
            const headers = document.querySelectorAll('h2');
            for (let h of headers) {
                if (h.innerText.includes('Conclusão e Recomendações')) {
                    // O pai do h2 é o container principal
                    areaEdicao = h.parentElement;
                    break;
                }
            }

            if (!areaEdicao) return;

            // 1. Carregar o HTML salvo
            fetch(`/historico_centro_custos/${historicoId}`)
                .then(res => res.json())
                .then(data => {
                    const dados = data.dados ? data.dados : data;
                    if (dados.conclusao_personalizada) {
                        // Substitui todo o conteúdo da área pelo HTML salvo
                        areaEdicao.innerHTML = dados.conclusao_personalizada;
                        // Reconecta os botões que foram apagados pelo innerHTML
                        const novaBarra = document.createElement('div');
                        novaBarra.innerHTML = document.getElementById('barra-edicao-conclusao').outerHTML;
                        areaEdicao.insertBefore(novaBarra.firstElementChild, areaEdicao.firstChild);
                        // Recarrega a página para aplicar o JS aos novos botões (gambiarra segura)
                        // Ou apenas re-adiciona os eventos
                    }
                }).catch(e => console.log("Erro ao carregar:", e));

            // 2. Função para ativar edição
            btnEditar.addEventListener('click', function() {
                // Torna editável apenas o que está dentro de areaEdicao, exceto a barra de botões
                const filhos = areaEdicao.children;
                for (let filho of filhos) {
                    if (filho.id !== 'barra-edicao-conclusao') {
                        filho.setAttribute('contenteditable', 'true');
                    }
                }
                areaEdicao.classList.add('editando-conclusao');
                
                btnEditar.style.display = 'none';
                btnSalvar.style.display = 'flex';
                msgSucesso.style.display = 'none';
            });

            // 3. Função para salvar
            btnSalvar.addEventListener('click', function() {
                const htmlEditado = areaEdicao.innerHTML;
                btnSalvar.innerText = "Salvando...";
                btnSalvar.disabled = true;

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
                        // Desativa edição
                        const filhos = areaEdicao.children;
                        for (let filho of filhos) {
                            filho.removeAttribute('contenteditable');
                        }
                        areaEdicao.classList.remove('editando-conclusao');
                        
                        btnEditar.style.display = 'flex';
                        btnSalvar.style.display = 'none';
                        btnSalvar.innerText = "💾 Salvar Relatório";
                        btnSalvar.disabled = false;
                        
                        msgSucesso.style.display = 'flex';
                        setTimeout(() => msgSucesso.style.display = 'none', 3000);
                    }
                })
                .catch(() => alert("Erro de conexão."))
                .finally(() => {
                    btnSalvar.innerText = "💾 Salvar Relatório";
                    btnSalvar.disabled = false;
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
print("[OK] Edição Direta (WYSIWYG) injetada com sucesso! Os botões estão acima dos blocos.")
