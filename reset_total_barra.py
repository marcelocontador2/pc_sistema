import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_barra_limpa_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Encontra o bloco da barra de botões e substitui TODO o conteúdo interno
# A barra começa com <div class="top-bar"> e termina com </div>
padrao_barra = r'(<div class="top-bar">).*?(</div>)'

nova_barra = '''<div class="top-bar">
        <!-- Recriando os botões do zero com onclick direto e isolado -->
        <button class="btn" style="background:#ed8936;" onclick="window.location.href='/'">← Voltar</button>
        <button class="btn" style="background:#38a169;" onclick="exibirSelecionado()">Exibir Selecionado</button>
        <button class="btn" style="background:#e53e3e;" onclick="excluirSelecionado()">Excluir Selecionado</button>
        <button class="btn btn-pdf" onclick="gerarPDFPanorama()">Gerar PDF</button>
        <button class="btn" style="background:#38a169;" onclick="salvarPanorama()">Confirmar e Salvar</button>
    </div>'''

if re.search(padrao_barra, c, flags=re.DOTALL):
    c = re.sub(padrao_barra, nova_barra, c, flags=re.DOTALL)
    print("[OK] Barra de botões totalmente recriada no HTML!")
else:
    print("[AVISO] Não encontrei a <div class='top-bar'>. Tentando substituir botão por botão...")
    # Fallback: substitui botões individuais
    c = re.sub(r'<a[^>]*Voltar[^>]*>.*?</a>', '<button class="btn" style="background:#ed8936;" onclick="window.location.href=\'/\'">← Voltar</button>', c, flags=re.DOTALL | re.IGNORECASE)
    c = re.sub(r'<button[^>]*>.*?Gerar PDF.*?</button>', '<button class="btn btn-pdf" onclick="gerarPDFPanorama()">Gerar PDF</button>', c, flags=re.DOTALL | re.IGNORECASE)

# 2. Remove QUALQUER script antigo que adicionava eventos aos botões
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const botoes.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnVoltar.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const btnPdf.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*// Seleciona todos os botões.*?</script>', '', c, flags=re.DOTALL)

# 3. Injeta a função do PDF no final do arquivo (com proteção para não duplicar)
if "function gerarPDFPanorama()" not in c:
    script_final = """
    <script>
        // Função isolada do PDF, sem eventos amarrados ao DOMContentLoaded
        function gerarPDFPanorama() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) {
                alert("Atenção: Marque um relatório no histórico antes de gerar o PDF.");
                return;
            }
            window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
        }
    </script>
    """
    c = c.replace('</body>', script_final + '\n</body>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botões reconstruídos e funções limpas!")
