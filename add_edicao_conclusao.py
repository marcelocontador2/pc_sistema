import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(arquivo, f"{arquivo}.bak_edit_{ts}")

c = open(arquivo, encoding='utf-8').read()

# 1. Injeta o botão "Editar Conclusão" e "Salvar Relatório" logo antes do fechamento da tag body
botoes = """
    <!-- Barra de Ações do Relatório -->
    <div id="barra-edicao" style="position: fixed; bottom: 20px; right: 20px; display: flex; gap: 10px; z-index: 9999;">
        <button id="btn-editar-conclusao" style="background: #3182ce; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">✏️ Editar Conclusão</button>
        <button id="btn-salvar-relatorio" style="background: #38a169; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: none;">💾 Salvar Relatório</button>
    </div>
"""

# 2. Injeta o script que habilita a edição e salva no backend
script_edicao = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            const btnEditar = document.getElementById('btn-editar-conclusao');
            const btnSalvar = document.getElementById('btn-salvar-relatorio');
            
            // Tenta achar a seção de conclusão (procura pela palavra "Conclusão" nos títulos)
            let conclusaoDiv = null;
            const headers = document.querySelectorAll('h2, h3, h4');
            for (let h of headers) {
                if (h.innerText.toUpperCase().includes('CONCLUSÃO') || h.innerText.toUpperCase().includes('RECOMENDAÇÕES')) {
                    conclusaoDiv = h.parentElement;
                    break;
                }
            }
            
            // Se não achou no HTML original, cria uma área no final
            if (!conclusaoDiv) {
                conclusaoDiv = document.createElement('div');
                conclusaoDiv.id = 'area-conclusao';
                conclusaoDiv.innerHTML = '<h2>Conclusão e Recomendações</h2><div id="texto-conclusao">...</div>';
                document.body.appendChild(conclusaoDiv);
            }

            btnEditar.addEventListener('click', function() {
                // Torna o texto editável
                const texto = conclusaoDiv.querySelector('p') || conclusaoDiv.querySelector('div') || conclusaoDiv;
                texto.setAttribute('contenteditable', 'true');
                texto.style.border = '2px dashed #3182ce';
                texto.style.padding = '10px';
                texto.focus();
                
                btnEditar.style.display = 'none';
                btnSalvar.style.display = 'block';
            });

            btnSalvar.addEventListener('click', async function() {
                if (!historicoId) {
                    alert("Para salvar, você precisa estar visualizando um histórico.");
                    return;
                }
                
                const texto = conclusaoDiv.querySelector('p') || conclusaoDiv.querySelector('div') || conclusaoDiv;
                const novoTexto = texto.innerText;
                
                btnSalvar.innerText = "Salvando...";
                
                try {
                    const res = await fetch(`/salvar_conclusao_centro_custos/${historicoId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ texto: novoTexto })
                    });
                    const data = await res.json();
                    
                    if (data.erro) {
                        alert("Erro ao salvar: " + data.mensagem);
                    } else {
                        alert("Conclusão salva com sucesso! O PDF usará este texto.");
                        texto.removeAttribute('contenteditable');
                        texto.style.border = 'none';
                        texto.style.padding = '0';
                        btnEditar.style.display = 'block';
                        btnSalvar.style.display = 'none';
                        btnSalvar.innerText = "💾 Salvar Relatório";
                    }
                } catch (e) {
                    alert("Erro de conexão ao salvar.");
                }
            });
        });
    </script>
"""

# 3. Injeta o espião para carregar a conclusão personalizada, se existir
espiao_conclusao = """
    <script id="carregar_conclusao_customizada">
        (function() {
            const originalFetch = window.fetch;
            window.fetch = function(url, options) {
                return originalFetch(url, options).then(res => res.clone().json()).then(data => {
                    if (data.conclusao_personalizada) {
                        // Assim que a página carregar, joga o texto personalizado na tela
                        setTimeout(() => {
                            const headers = document.querySelectorAll('h2, h3');
                            for (let h of headers) {
                                if (h.innerText.toUpperCase().includes('CONCLUSÃO') || h.innerText.toUpperCase().includes('RECOMENDAÇÕES')) {
                                    const div = h.parentElement;
                                    const texto = div.querySelector('p') || div.querySelector('div') || div;
                                    texto.innerHTML = data.conclusao_personalizada.replace(/\\n/g, '<br>');
                                    break;
                                }
                            }
                        }, 500);
                    }
                    return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } });
                });
            };
        })();
    </script>
"""

# Adiciona os botões e scripts no final da página
if '</body>' in c:
    c = c.replace('</body>', botoes + '\n' + espiao_conclusao + '\n' + script_edicao + '\n</body>', 1)
else:
    c += botoes + '\n' + espiao_conclusao + '\n' + script_edicao

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botões de Edição e Salvar injetados no relatório!")
