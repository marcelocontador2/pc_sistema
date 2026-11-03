import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_botoes_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove TODOS os onclick dos botões da barra de ações
c = re.sub(r'onclick="[^"]*"', '', c)

# 2. Injeta o script final no fim da página para ligar os botões corretamente
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Acha todos os botões da página
            const botoes = Array.from(document.querySelectorAll('button'));

            // Função auxiliar para encontrar o botão pelo texto
            function acharBotao(texto) {
                return botoes.find(b => b.innerText.trim().toUpperCase().includes(texto.toUpperCase()));
            }

            // Configura o botão Voltar
            const btnVoltar = acharBotao('VOLTAR');
            if (btnVoltar) {
                btnVoltar.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.location.href = '/';
                });
            }

            // Configura o botão Gerar PDF (com a proteção contra duplo clique)
            const btnPdf = acharBotao('GERAR PDF');
            if (btnPdf) {
                // Clona o botão para garantir que nenhum evento antigo fique atrelado
                const novoBtnPdf = btnPdf.cloneNode(true);
                btnPdf.parentNode.replaceChild(novoBtnPdf, btnPdf);
                
                novoBtnPdf.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const check = document.querySelector(".check-historico:checked");
                    if (!check) {
                        alert("Atenção: Marque um relatório no histórico antes de gerar o PDF.");
                        return;
                    }
                    
                    const url = `/gerar_pdf_panorama/${check.value}`;
                    window.open(url, '_blank');
                });
            }

            // (Opcional) Se quiser garantir que os outros botões funcionem sem conflito:
            const btnExibir = acharBotao('EXIBIR');
            if (btnExibir) btnExibir.addEventListener('click', () => { if(typeof exibirSelecionado === 'function') exibirSelecionado(); });

            const btnExcluir = acharBotao('EXCLUIR');
            if (btnExcluir) btnExcluir.addEventListener('click', () => { if(typeof excluirSelecionado === 'function') excluirSelecionado(); });

            const btnSalvar = acharBotao('CONFIRMAR');
            if (btnSalvar) btnSalvar.addEventListener('click', () => { if(typeof salvarPanorama === 'function') salvarPanorama(); });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botões do Panorama reconfigurados e isolados (sem conflito)!")
