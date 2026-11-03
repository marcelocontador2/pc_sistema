import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_edit_wysiwyg_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa scripts de edição anteriores
c = re.sub(r'<script id="js-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-tela">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)

# 2. Modifica a função preencherConclusao para respeitar o texto personalizado
# Procura a linha que define a função
if 'window.conclusaoPersonalizada' not in c:
    c = c.replace(
        'function preencherConclusao(d) {',
        '''function preencherConclusao(d) {
            // Se existe conclusão personalizada salva, NÃO sobrescreve os blocos
            if (window.conclusaoPersonalizada) {
                return;
            }'''
    )

# 3. Adiciona o CSS para a área editável
css_edit = """
    <style>
        .editando-conclusao {
            outline: 3px dashed #f59e0b !important;
            outline-offset: 3px;
            background-color: #fffbeb !important;
            padding: 10px !important;
            border-radius: 6px !important;
            min-height: 40px;
        }
        @media print {
            #barra-edicao-conclusao { display: none !important; }
            .editando-conclusao { outline: none !important; background-color: transparent !important; padding: 0 !important; }
        }
    </style>
"""
if '</head>' in c:
    c = c.replace('</head>', css_edit + '\n</head>', 1)

# 4. Adiciona o script de edição DIRETA (WYSIWYG)
script_edit = """
    <script id="js-edicao-direta-wysiwyg">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');

            const btnEditar = document.getElementById('btn-editar-conclusao');
            const btnSalvar = document.getElementById('btn-salvar-conclusao');
            const msgSucesso = document.getElementById('msg-conclusao');

            // IDs dos blocos que serão editados
            const idsBlocos = ['conclusao-total', 'conclusao-concentracao', 'conclusao-alertas', 'conclusao-recomendacoes'];

            // 1. Carregar a conclusão personalizada do histórico (se existir)
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
                                // Marca globalmente que temos conclusão personalizada
                                window.conclusaoPersonalizada = htmlSalvo;
                            } catch(e) {
                                console.log("Formato antigo, aplicando como texto simples:", e);
                                // Se for uma versão antiga (texto puro), apenas ignora
                            }
                        }
                    })
                    .catch(e => console.log("Erro ao buscar conclusão:", e));
            }

            // 2. Botão Editar: Ativa contenteditable nos blocos
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

            // 3. Botão Salvar: Pega o conteúdo e envia para o backend
            btnSalvar.addEventListener('click', function() {
                if (!historicoId) {
                    alert("Você precisa estar visualizando um histórico para salvar.");
                    return;
                }

                // Monta o objeto com o HTML de cada bloco
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
                        // Desativa edição
                        for (const id of idsBlocos) {
                            const el = document.getElementById(id);
                            if (el) {
                                el.removeAttribute('contenteditable');
                                el.classList.remove('editando-conclusao');
                            }
                        }
                        // Marca como personalizado para o preencherConclusao não sobrescrever
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
print("[OK] Edição WYSIWYG (direto nos blocos) injetada com sucesso!")
