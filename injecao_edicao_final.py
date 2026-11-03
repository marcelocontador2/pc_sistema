import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_edicao_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove qualquer script anterior de edição para não conflitar
c = re.sub(r'<script id="sistema-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# Cria o bloco HTML de edição e a lógica JS
bloco_edicao = """
    <!-- SISTEMA DE EDIÇÃO DA CONCLUSÃO -->
    <div id="bloco-conclusao" style="margin-top: 40px; border-top: 2px dashed #cbd5e0; padding-top: 20px;">
        <h2 style="color: #0a1c3a; font-size: 18px; margin-bottom: 10px;">Conclusão e Recomendações</h2>
        
        <!-- Esta div será impressa no PDF -->
        <div id="conclusao-print" style="display: none; white-space: pre-wrap; font-size: 14px; line-height: 1.6; text-align: justify; color: #333;"></div>
        
        <!-- Este textarea e botão aparecem só na tela do navegador -->
        <textarea id="conclusao-edit" placeholder="Digite aqui a conclusão do relatório..." style="width: 100%; height: 120px; padding: 10px; font-family: inherit; font-size: 14px; border: 1px solid #cbd5e0; border-radius: 6px; resize: vertical; outline: none;"></textarea>
        
        <div style="margin-top: 10px; display: flex; align-items: center; gap: 10px;">
            <button id="btn-salvar-conclusao" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">💾 Salvar Relatório</button>
            <span id="msg-salvo" style="display: none; color: #38a169; font-weight: bold;">✓ Salvo com sucesso!</span>
        </div>
    </div>

    <style>
        @media print {
            /* Esconde a área de edição na hora de imprimir, mas mostra o texto final */
            #conclusao-edit, #btn-salvar-conclusao, #msg-salvo { display: none !important; }
            #conclusao-print { display: block !important; }
            #bloco-conclusao { border-top: none !important; margin-top: 20px !important; padding-top: 0 !important; page-break-inside: avoid !important; }
        }
    </style>

    <script id="sistema-edicao-conclusao">
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            const textarea = document.getElementById('conclusao-edit');
            const divPrint = document.getElementById('conclusao-print');
            const btnSalvar = document.getElementById('btn-salvar-conclusao');
            const msgSalvo = document.getElementById('msg-salvo');

            // 1. Carrega o texto salvo anteriormente, se existir
            if (historicoId) {
                fetch(`/historico_centro_custos/${historicoId}`)
                    .then(res => res.json())
                    .then(data => {
                        const dados = data.dados ? data.dados : data;
                        if (dados.conclusao_personalizada) {
                            textarea.value = dados.conclusao_personalizada;
                            divPrint.innerText = dados.conclusao_personalizada;
                        }
                    }).catch(e => console.log("Erro ao carregar conclusão:", e));
            }

            // 2. Função para salvar
            btnSalvar.addEventListener('click', function() {
                const texto = textarea.value.trim();
                
                if (!historicoId) {
                    alert("Erro: Nenhum histórico selecionado para salvar.");
                    return;
                }

                btnSalvar.innerText = "Salvando...";
                btnSalvar.disabled = true;

                fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ texto: texto })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.erro) {
                        alert("Erro: " + data.mensagem);
                    } else {
                        divPrint.innerText = texto;
                        msgSalvo.style.display = 'inline';
                        setTimeout(() => { msgSalvo.style.display = 'none'; }, 3000);
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

# Injeta o bloco antes do fechamento do body
if '</body>' in c:
    c = c.replace('</body>', bloco_edicao + '\n</body>', 1)
else:
    c += bloco_edicao

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Sistema de edição da conclusão injetado no final do relatório!")
