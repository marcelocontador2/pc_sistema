import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"

# Backup
shutil.copy2(arquivo, f"{arquivo}.bak_edit_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa QUALQUER script de edição anterior que possa ter ficado
c = re.sub(r'<div id="modal-conclusao".*?</div>\s*</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="barra-edicao".*?</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-direta">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="sistema-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# 2. Cria o Botão Flutuante e o Modal (sempre visível)
html_edicao = """
    <!-- BOTÃO FLUTUANTE DE EDIÇÃO -->
    <button id="btn-abrir-edicao" style="position: fixed; bottom: 30px; right: 30px; background: #f59e0b; color: white; border: none; padding: 12px 24px; border-radius: 50px; font-weight: bold; font-size: 16px; cursor: pointer; z-index: 99999; box-shadow: 0 4px 15px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 8px;">
        ✏️ Editar Conclusão
    </button>

    <!-- MODAL DE EDIÇÃO -->
    <div id="modal-edicao-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 100000; justify-content: center; align-items: center;">
        <div style="background: #fff; padding: 25px; border-radius: 12px; width: 800px; max-width: 90%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #1a202c; font-size: 22px; display: flex; align-items: center; gap: 10px;">✏️ Editar Conclusão e Recomendações</h3>
            <p style="font-size: 14px; color: #718096; margin-bottom: 15px;">Altere o texto abaixo. As formatações e os botões não aparecerão no PDF final.</p>
            
            <textarea id="texto-conclusao-edit" style="flex: 1; min-height: 350px; width: 100%; padding: 15px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; line-height: 1.6; resize: vertical; outline: none; background: #f8fafc;"></textarea>
            
            <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 12px;">
                <button id="btn-fechar-edicao" style="padding: 10px 20px; border: none; border-radius: 6px; background: #e2e8f0; color: #4a5568; font-weight: bold; cursor: pointer; font-size: 15px;">Cancelar</button>
                <button id="btn-salvar-edicao" style="padding: 10px 20px; border: none; border-radius: 6px; background: #38a169; color: white; font-weight: bold; cursor: pointer; font-size: 15px;">💾 Salvar Conclusão</button>
            </div>
        </div>
    </div>

    <style>
        @media print {
            #btn-abrir-edicao, #modal-edicao-conclusao { display: none !important; }
        }
    </style>
"""

# 3. Adiciona a Lógica JS (Abre o Modal, Puxa o Texto e Salva)
js_edicao = """
    <script id="js-edicao-conclusao">
        document.addEventListener('DOMContentLoaded', function() {
            const btnAbrir = document.getElementById('btn-abrir-edicao');
            const modal = document.getElementById('modal-edicao-conclusao');
            const btnFechar = document.getElementById('btn-fechar-edicao');
            const btnSalvar = document.getElementById('btn-salvar-edicao');
            const textarea = document.getElementById('texto-conclusao-edit');

            // 1. Abre o Modal e carrega o texto que já está na tela (ou no banco)
            btnAbrir.addEventListener('click', function() {
                const urlParams = new URLSearchParams(window.location.search);
                const historicoId = urlParams.get('historico_id');

                modal.style.display = 'flex';
                textarea.value = "Carregando texto...";
                textarea.disabled = true;

                // Se tiver ID do histórico, busca o texto salvo no banco
                if (historicoId) {
                    fetch(`/historico_centro_custos/${historicoId}`)
                        .then(res => res.json())
                        .then(data => {
                            const dados = data.dados ? data.dados : data;
                            if (dados.conclusao_personalizada) {
                                textarea.value = dados.conclusao_personalizada;
                            } else {
                                // Se não tiver salvo, pega o texto que está renderizado na tela atual
                                textarea.value = extrairTextoDaTela();
                            }
                        })
                        .catch(e => {
                            console.error(e);
                            textarea.value = extrairTextoDaTela();
                        })
                        .finally(() => {
                            textarea.disabled = false;
                        });
                } else {
                    // Se não tiver ID (ex: acesso direto), pega o texto da tela
                    textarea.value = extrairTextoDaTela();
                    textarea.disabled = false;
                }
            });

            // Função para pegar o texto dos blocos coloridos na tela
            function extrairTextoDaTela() {
                const headers = document.querySelectorAll('h1, h2, h3, h4');
                for (let h of headers) {
                    if (h.innerText.toUpperCase().includes('CONCLUSÃO') || h.innerText.toUpperCase().includes('RECOMENDAÇÕES')) {
                        const container = h.closest('.card') || h.parentElement;
                        // Remove os títulos para pegar só o texto descritivo
                        return container.innerText.replace('Conclusão e Recomendações', '').trim();
                    }
                }
                return "";
            }

            // 2. Fecha o Modal
            btnFechar.addEventListener('click', function() {
                modal.style.display = 'none';
            });

            // 3. Salva o texto no Banco de Dados
            btnSalvar.addEventListener('click', function() {
                const urlParams = new URLSearchParams(window.location.search);
                const historicoId = urlParams.get('historico_id');

                if (!historicoId) {
                    alert("Erro: Para salvar, você precisa estar visualizando um histórico.");
                    return;
                }

                const texto = textarea.value;
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
                        alert("Erro ao salvar: " + data.mensagem);
                    } else {
                        alert("Conclusão salva com sucesso! O PDF usará este texto.");
                        modal.style.display = 'none';
                        // Opcional: atualizar a tela na hora
                        const headers = document.querySelectorAll('h1, h2, h3, h4');
                        for (let h of headers) {
                            if (h.innerText.toUpperCase().includes('CONCLUSÃO') || h.innerText.toUpperCase().includes('RECOMENDAÇÕES')) {
                                const container = h.closest('.card') || h.parentElement;
                                container.innerHTML = `<h2>Conclusão e Recomendações</h2><div style="white-space: pre-wrap; line-height: 1.6;">${texto}</div>`;
                                break;
                            }
                        }
                    }
                })
                .catch(() => alert("Erro de conexão ao salvar."))
                .finally(() => {
                    btnSalvar.innerText = "💾 Salvar Conclusão";
                    btnSalvar.disabled = false;
                });
            });
        });
    </script>
"""

# Injeta tudo antes do </body>
if '</body>' in c:
    c = c.replace('</body>', html_edicao + '\n' + js_edicao + '\n</body>', 1)
else:
    c += html_edicao + '\n' + js_edicao

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Sistema de Edição Injetado! O botão flutuante aparecerá no canto da tela do relatório.")
