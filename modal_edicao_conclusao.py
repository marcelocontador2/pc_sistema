import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(arquivo, f"{arquivo}.bak_modal_edicao_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove qualquer botão anterior de "Editar Conclusão" para não duplicar
c = re.sub(r'<button[^>]*id="btn-editar-conclusao".*?</button>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="modal-conclusao".*?</div>\s*</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-edicao-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# 2. Adiciona o botão "Editar Conclusão" ao lado do "Gerar PDF"
# Procura o botão de Gerar PDF existente
match_pdf = re.search(r'(<button[^>]*>Gerar PDF</button>)', c, re.IGNORECASE)
if match_pdf:
    btn_pdf = match_pdf.group(1)
    novo_btn = btn_pdf + '\n        <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-left: 10px;">✏️ Editar Conclusão</button>'
    c = c.replace(btn_pdf, novo_btn, 1)
else:
    # Fallback: adiciona perto do fim do body
    c = c.replace('</body>', '<button id="btn-editar-conclusao" style="position:fixed; bottom:20px; right:20px; background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; z-index:9999;">✏️ Editar Conclusão</button>\n</body>', 1)

# 3. Adiciona o modal e a lógica JavaScript
modal_html = """
    <!-- MODAL DE EDIÇÃO DE CONCLUSÃO -->
    <div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; justify-content: center; align-items: center;">
        <div style="background: #fff; padding: 25px; border-radius: 10px; width: 800px; max-width: 90%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
            <h3 style="margin-top: 0; color: #1a202c; font-size: 20px;">✏️ Editar Conclusão e Recomendações</h3>
            <p style="font-size: 14px; color: #718096; margin-bottom: 15px;">Altere o texto abaixo. Ele será usado no PDF gerado.</p>
            
            <textarea id="texto-conclusao-modal" style="flex: 1; min-height: 300px; width: 100%; padding: 15px; border: 1px solid #cbd5e0; border-radius: 6px; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6; resize: vertical; outline: none;"></textarea>
            
            <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px;">
                <button id="btn-cancelar-conclusao" style="padding: 10px 20px; border: none; border-radius: 6px; background: #e2e8f0; color: #4a5568; font-weight: bold; cursor: pointer;">Cancelar</button>
                <button id="btn-salvar-conclusao-modal" style="padding: 10px 20px; border: none; border-radius: 6px; background: #38a169; color: white; font-weight: bold; cursor: pointer;">💾 Salvar Conclusão</button>
            </div>
        </div>
    </div>
"""

# Adiciona o modal e o script antes do </body>
script_modal = """
    <script>
        document.getElementById('btn-editar-conclusao').addEventListener('click', function() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) {
                alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
                return;
            }
            
            const id = check.value;
            
            // Abre o modal
            const modal = document.getElementById('modal-conclusao');
            modal.style.display = 'flex';
            
            const textarea = document.getElementById('texto-conclusao-modal');
            textarea.value = "Carregando...";
            
            // Busca o texto atual salvo no histórico
            fetch(`/historico_centro_custos/${id}`)
                .then(res => res.json())
                .then(data => {
                    const dados = data.dados ? data.dados : data;
                    if (dados.conclusao_personalizada) {
                        textarea.value = dados.conclusao_personalizada;
                    } else {
                        textarea.value = "";
                        textarea.placeholder = "Nenhuma conclusão salva ainda. Digite a sua aqui...";
                    }
                })
                .catch(() => {
                    textarea.value = "";
                    alert("Erro ao carregar o texto anterior.");
                });
        });

        document.getElementById('btn-cancelar-conclusao').addEventListener('click', function() {
            document.getElementById('modal-conclusao').style.display = 'none';
        });

        document.getElementById('btn-salvar-conclusao-modal').addEventListener('click', function() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) return;
            
            const id = check.value;
            const texto = document.getElementById('texto-conclusao-modal').value;
            const btn = document.getElementById('btn-salvar-conclusao-modal');
            
            btn.innerText = "Salvando...";
            btn.disabled = true;

            fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: texto })
            })
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    alert("Erro: " + data.mensagem);
                } else {
                    alert("Conclusão salva com sucesso! Agora você pode gerar o PDF.");
                    document.getElementById('modal-conclusao').style.display = 'none';
                }
            })
            .catch(() => alert("Erro de conexão."))
            .finally(() => {
                btn.innerText = "💾 Salvar Conclusão";
                btn.disabled = false;
            });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', modal_html + '\n' + script_modal + '\n</body>', 1)
else:
    c += modal_html + '\n' + script_modal

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Editar Conclusão' e Modal adicionados na tela principal!")
