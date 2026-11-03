import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_reset_btn_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa qualquer resquício de onclick ou script de botões que tentamos antes
c = re.sub(r'onclick="[^"]*"', '', c, flags=re.IGNORECASE)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const botoes.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnVoltar.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf.*?</script>', '', c, flags=re.DOTALL)

# 2. Script Universal Definitivo
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Seleciona todos os botões da página
            const botoes = document.querySelectorAll('button');

            botoes.forEach(function(btn) {
                // O SEGREDO: Clonar o botão destrói TODOS os eventos antigos e onclick!
                const novoBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(novoBtn, btn);

                // Pega o texto do botão e transforma em maiúsculo
                const texto = novoBtn.innerText.trim().toUpperCase();

                // 1. VOLTAR
                if (texto.includes('VOLTAR')) {
                    novoBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        window.location.href = '/'; // Vai para a home
                    });
                }
                
                // 2. GERAR PDF
                else if (texto.includes('GERAR PDF')) {
                    novoBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        const check = document.querySelector('.check-historico:checked');
                        if (!check) {
                            alert("Atenção: Marque um relatório no histórico antes de gerar o PDF.");
                            return;
                        }
                        window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
                    });
                }

                // 3. EXIBIR
                else if (texto.includes('EXIBIR')) {
                    novoBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (typeof exibirSelecionado === 'function') exibirSelecionado();
                    });
                }

                // 4. EXCLUIR
                else if (texto.includes('EXCLUIR')) {
                    novoBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (typeof excluirSelecionado === 'function') excluirSelecionado();
                    });
                }

                // 5. CONFIRMAR E SALVAR
                else if (texto.includes('CONFIRMAR')) {
                    novoBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (typeof salvarPanorama === 'function') salvarPanorama();
                    });
                }
            });
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botões resetados via clonagem. Voltar e PDF separados com sucesso!")
