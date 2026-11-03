import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_solucao_def_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa qualquer script de edição anterior que possa ter ficado
c = re.sub(r'<script id="js-edicao-direta-wysiwyg">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-tela">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="barra-edicao-conclusao".*?</div>', '', c, flags=re.DOTALL)

# 2. Adiciona o CSS para limpar o PDF e estilizar a edição
css_fix = """
    <style>
        /* Esconde ícones e caracteres estranhos na impressão e na tela */
        i, .fa, .fas, .far, .fal, .fad, .material-icons, [class^="icon-"], [class*=" icon-"] {
            display: none !important;
        }
        
        /* Estilo da barra de edição */
        #barra-edicao-conclusao {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            margin-top: 20px;
            padding: 10px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }

        /* Estilo da área editável */
        .editando-conclusao {
            outline: 3px dashed #f59e0b !important;
            outline-offset: 3px;
            background-color: #fffbeb !important;
            padding: 10px !important;
            border-radius: 6px !important;
            min-height: 40px;
            cursor: text;
        }
        
        /* Regras de impressão */
        @media print {
            #barra-edicao-conclusao { display: none !important; }
            .editando-conclusao { outline: none !important; background-color: transparent !important; padding: 0 !important; }
        }
    </style>
"""
if '</head>' in c:
    c = c.replace('</head>', css_fix + '\n</head>', 1)

# 3. Injeta a barra de botões antes do título de conclusão
# O título pode estar como <h2> ou h1. Vamos buscar o container principal
if 'id="barra-edicao-conclusao"' not in c:
    toolbar = """
    <div id="barra-edicao-conclusao">
        <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 14px;">✏️ Editar Conclusão</button>
        <button id="btn-salvar-conclusao" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; display: none; align-items: center; gap: 8px; font-size: 14px;">💾 Salvar Relatório</button>
        <span id="msg-conclusao" style="display: none; color: #38a169; font-weight: bold; align-items: center;">✓ Salvo com sucesso!</span>
    </div>
    """
    # Procura o primeiro h2 que tenha Conclusão ou Recomendações
    c = re.sub(r'(<h[1-3][^>]*>.*?(?:Conclusão|Recomendações).*?</h[1-3]>)', toolbar + r'\1', c, flags=re.IGNORECASE)

# 4. Adiciona o Script de Edição e Salvamento
js_fix = """
    <script id="js-edicao-final">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');

            const btnEditar = document.getElementById('btn-editar-conclusao');
            const btnSalvar = document.getElementById('btn-salvar-conclusao');
            const msgSucesso = document.getElementById('msg-conclusao');

            // IDs dos blocos que serão editados
            const idsBlocos = ['conclusao-total', 'conclusao-concentracao', 'conclusao-alertas', 'conclusao-recomendacoes'];

            // 1. Carregar a conclusão personalizada do histórico
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
                                
                                // Aplica em cada bloco
                                for (const id of idsBlocos) {
                                    if (htmlSalvo[id]) {
                                        document.getElementById(id).innerHTML = htmlSalvo[id];
                                    }
                                }
                                // Marca globalmente para o preencherConclusao não sobrescrever
                                window.conclusaoPersonalizada = htmlSalvo;
                            } catch(e) {
                                console.log("Aviso: Erro ao ler conclusão personalizada.", e);
                            }
                        }
                    })
                    .catch(e => console.log("Erro ao buscar histórico:", e));
            }

            // 2. Ativar Modo de Edição
            if (btnEditar) {
                btnEditar.addEventListener('click', function() {
                    for (const id of idsBlocos) {
                        const el = document.getElementById(id);
                        if (el) {
                            el.setAttribute('contenteditable', 'true');
                            el.classList.add('editando-conclusao');
                        }
                    }
                    btnEditar.style.display = 'none';
                    btnSalvar.style.display = 'flex';
                    if (msgSucesso) msgSucesso.style.display = 'none';
                });
            }

            // 3. Salvar
            if (btnSalvar) {
                btnSalvar.addEventListener('click', function() {
                    if (!historicoId) {
                        alert("Erro: Você precisa estar visualizando um histórico para salvar.");
                        return;
                    }

                    const htmlEditado = {};
                    for (const id of idsBlocos) {
                        const el = document.getElementById(id);
                        if (el) {
                            htmlEditado[id] = el.innerHTML;
                        }
                    }

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
                            for (const id of idsBlocos) {
                                const el = document.getElementById(id);
                                if (el) {
                                    el.removeAttribute('contenteditable');
                                    el.classList.remove('editando-conclusao');
                                }
                            }
                            // Garante que a função original não apague o texto na próxima renderização
                            window.conclusaoPersonalizada = htmlEditado;
                            
                            btnEditar.style.display = 'flex';
                            btnSalvar.style.display = 'none';
                            btnSalvar.innerText = "💾 Salvar Relatório";
                            btnSalvar.disabled = false;
                            
                            if (msgSucesso) {
                                msgSucesso.style.display = 'flex';
                                setTimeout(() => msgSucesso.style.display = 'none', 3000);
                            }
                        }
                    })
                    .catch(() => alert("Erro de conexão ao salvar."))
                    .finally(() => {
                        btnSalvar.innerText = "💾 Salvar Relatório";
                        btnSalvar.disabled = false;
                    });
                });
            }
        });

        // 4. "Blindar" a função preencherConclusao original
        // Impede que ela sobrescreva o texto editado quando a página for impressa
        const timeoutPreencher = setInterval(() => {
            if (window.preencherConclusao) {
                const original = window.preencherConclusao;
                window.preencherConclusao = function(d) {
                    if (window.conclusaoPersonalizada) {
                        console.log("Conclusão personalizada ativa. Ignorando texto automático.");
                        return;
                    }
                    original(d);
                };
                clearInterval(timeoutPreencher);
            }
        }, 100);
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', js_fix + '\n</body>', 1)
else:
    c += js_fix

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Sistema de edição final injetado e caracteres estranhos removidos!")
