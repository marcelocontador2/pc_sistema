import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_auditoria_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove contenteditable="true" dos parágrafos (limpa lixo de tentativas antigas)
c = c.replace('contenteditable="true"', '')

# 2. Remove barra antiga (vazia) que ficou no HTML
c = c.replace('<!-- BARRA DE EDIÇÃO DIRETA -->', '')

# 3. Remove scripts antigos de edição
c = re.sub(r'<script id="script-edicao-definitivo">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-final">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-direta-wysiwyg">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-tela">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)

# 4. Adiciona a barra de botões EXATAMENTE após o h2 real
barra_html = '''
    <div id="barra-edicao-conclusao" style="display: flex; gap: 10px; margin-bottom: 20px; padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
        <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px;">✏️ Editar Conclusão</button>
        <button id="btn-salvar-conclusao" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; display: none;">💾 Salvar Relatório</button>
        <span id="msg-conclusao" style="display: none; color: #38a169; font-weight: bold; align-items: center;">✓ Salvo com sucesso!</span>
    </div>
'''

# Substitui a barra antiga vazia pela nova, logo após o h2 de conclusão
c = c.replace(
    '<h2 class="section-title">Conclusão e Recomendações</h2>',
    '<h2 class="section-title">Conclusão e Recomendações</h2>\n' + barra_html
)

# 5. Adiciona o CSS para a área editável
css = """
    <style>
        .editando-conclusao {
            outline: 3px dashed #f59e0b !important;
            outline-offset: 3px;
            background-color: #fffbeb !important;
            padding: 10px !important;
            border-radius: 6px !important;
        }
        @media print {
            #barra-edicao-conclusao { display: none !important; }
            .editando-conclusao { outline: none !important; background-color: transparent !important; padding: 0 !important; }
        }
    </style>
"""
c = c.replace('</head>', css + '\n</head>', 1)

# 6. Script de edição e salvamento correto
js = """
    <script id="js-edicao-final-real">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');

            const btnEditar = document.getElementById('btn-editar-conclusao');
            const btnSalvar = document.getElementById('btn-salvar-conclusao');
            const msgSucesso = document.getElementById('msg-conclusao');

            const blocos = ['conclusao-total', 'conclusao-concentracao', 'conclusao-alertas', 'conclusao-recomendacoes'];

            // Carregar texto personalizado do histórico (se existir)
            if (historicoId) {
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
                                console.log("Aviso: conclusão em formato antigo.", e);
                            }
                        }
                    }).catch(e => console.log("Erro ao carregar:", e));
            }

            // Botão Editar
            if (btnEditar) {
                btnEditar.addEventListener('click', function() {
                    blocos.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            el.setAttribute('contenteditable', 'true');
                            el.classList.add('editando-conclusao');
                        }
                    });
                    btnEditar.style.display = 'none';
                    btnSalvar.style.display = 'block';
                    if (msgSucesso) msgSucesso.style.display = 'none';
                });
            }

            // Botão Salvar
            if (btnSalvar) {
                btnSalvar.addEventListener('click', function() {
                    if (!historicoId) {
                        alert("Você precisa estar visualizando um histórico para salvar.");
                        return;
                    }

                    const htmlEditado = {};
                    blocos.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) htmlEditado[id] = el.innerHTML;
                    });

                    btnSalvar.innerText = "Salvando...";
                    btnSalvar.disabled = true;

                    fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ texto: JSON.stringify(htmlEditado) })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.erro) {
                            alert("Erro: " + data.mensagem);
                        } else {
                            blocos.forEach(id => {
                                const el = document.getElementById(id);
                                if (el) {
                                    el.removeAttribute('contenteditable');
                                    el.classList.remove('editando-conclusao');
                                }
                            });
                            window.conclusaoPersonalizada = htmlEditado;
                            btnEditar.style.display = 'block';
                            btnSalvar.style.display = 'none';
                            btnSalvar.innerText = "💾 Salvar Relatório";
                            btnSalvar.disabled = false;
                            if (msgSucesso) {
                                msgSucesso.style.display = 'flex';
                                setTimeout(() => msgSucesso.style.display = 'none', 3000);
                            }
                        }
                    })
                    .catch(() => alert("Erro de conexão."))
                    .finally(() => {
                        btnSalvar.innerText = "💾 Salvar Relatório";
                        btnSalvar.disabled = false;
                    });
                });
            }
        });

        // Bloquear sobrescrita automática da função preencherConclusao
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
c = c.replace('</body>', js + '\n</body>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Auditoria aplicada. Botões e edição corrigidos no lugar certo!")
