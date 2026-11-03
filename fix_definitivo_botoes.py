import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_fix_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Substitui a div da barra de botões por uma versão limpa, usando onclick nativo em cada botão
padrao_barra = r'<div class="top-bar">.*?</div>'
nova_barra = '''<div class="top-bar">
        <button class="btn" style="background:#ed8936;" onclick="window.location.href='/'">← Voltar</button>
        <button class="btn" style="background:#38a169;" onclick="if(typeof exibirSelecionado === 'function') exibirSelecionado()">Exibir Selecionado</button>
        <button class="btn" style="background:#e53e3e;" onclick="if(typeof excluirSelecionado === 'function') excluirSelecionado()">Excluir Selecionado</button>
        <button class="btn btn-pdf" onclick="gerarPDFPanorama()">Gerar PDF</button>
        <button class="btn" style="background:#38a169;" onclick="if(typeof salvarPanorama === 'function') salvarPanorama()">Confirmar e Salvar</button>
    </div>'''

if re.search(padrao_barra, c, flags=re.DOTALL | re.IGNORECASE):
    c = re.sub(padrao_barra, nova_barra, c, flags=re.DOTALL | re.IGNORECASE)
    print("[OK] Barra de botões substituída por versão estática limpa.")
else:
    print("[AVISO] Div top-bar não encontrada.")

# 2. Remove qualquer script que tente adicionar eventos aos botões (causadores de conflito)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{.*?</script>', '', c, flags=re.DOTALL)

# 3. Injeta a função do PDF de forma isolada e segura no final do arquivo, para garantir que ela existe
script_pdf = """
    <script>
        function gerarPDFPanorama() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
        }
    </script>
"""

# Adiciona o script do PDF antes do fechamento do body, se ainda não existir
if "function gerarPDFPanorama()" not in c:
    c = c.replace('</body>', script_pdf + '\n</body>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Scripts conflitantes removidos e função do PDF injetada!")
