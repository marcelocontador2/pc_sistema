import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_limpeza_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove qualquer script antigo que possa ter ficado (blocos DOMContentLoaded que mencionam botões)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const botoes = Array\.from.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf =.*?</script>', '', c, flags=re.DOTALL)

# 2. Limpa todos os onclick dos botões da barra de ações para evitar duplicidade
c = re.sub(r'onclick="[^"]*"', '', c, flags=re.IGNORECASE)

# 3. Recria os botões com IDs únicos (substituindo o texto interno deles)
c = re.sub(r'<button[^>]*>\s*(?:←\s*)?Voltar\s*</button>', '<button id="btn-voltar" class="btn" style="background:#ed8936;">← Voltar</button>', c, flags=re.IGNORECASE)
c = re.sub(r'<button[^>]*>\s*Exibir Selecionado\s*</button>', '<button id="btn-exibir" class="btn" style="background:#38a169;">Exibir Selecionado</button>', c, flags=re.IGNORECASE)
c = re.sub(r'<button[^>]*>\s*Excluir Selecionado\s*</button>', '<button id="btn-excluir" class="btn" style="background:#e53e3e;">Excluir Selecionado</button>', c, flags=re.IGNORECASE)
c = re.sub(r'<button[^>]*>\s*Gerar PDF\s*</button>', '<button id="btn-pdf" class="btn btn-pdf">Gerar PDF</button>', c, flags=re.IGNORECASE)
c = re.sub(r'<button[^>]*>\s*Confirmar e Salvar\s*</button>', '<button id="btn-salvar" class="btn" style="background:#38a169;">Confirmar e Salvar</button>', c, flags=re.IGNORECASE)

# 4. Injeta o script final e definitivo no final da página
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // 1. Botão Voltar (Vai para a Home)
            const btnVoltar = document.getElementById('btn-voltar');
            if (btnVoltar) {
                btnVoltar.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.location.href = '/';
                });
            }

            // 2. Botão Gerar PDF (Exige histórico e abre 1 aba)
            const btnPdf = document.getElementById('btn-pdf');
            if (btnPdf) {
                btnPdf.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const check = document.querySelector('.check-historico:checked');
                    if (!check) {
                        alert("Atenção: Marque um relatório no histórico antes de gerar o PDF.");
                        return;
                    }
                    
                    const url = `/gerar_pdf_panorama/${check.value}`;
                    window.open(url, '_blank');
                });
            }

            // 3. Botões de Ação da Tela
            const btnExibir = document.getElementById('btn-exibir');
            if (btnExibir) {
                btnExibir.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (typeof exibirSelecionado === 'function') exibirSelecionado();
                });
            }

            const btnExcluir = document.getElementById('btn-excluir');
            if (btnExcluir) {
                btnExcluir.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (typeof excluirSelecionado === 'function') excluirSelecionado();
                });
            }

            const btnSalvar = document.getElementById('btn-salvar');
            if (btnSalvar) {
                btnSalvar.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (typeof salvarPanorama === 'function') salvarPanorama();
                });
            }
        });
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Barra de botões completamente reescrita e isolada!")
