import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_fix_voltar_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Substitui o link <a> "Voltar" por um botão real com onclick direto
c = re.sub(
    r'<a[^>]*href="/"[^>]*>.*?Voltar.*?</a>',
    '<button class="btn" style="background:#ed8936;" onclick="window.location.href=\'/\'">← Voltar</button>',
    c, flags=re.IGNORECASE | re.DOTALL
)

# 2. Substitui o botão "Gerar PDF" para usar onclick direto
c = re.sub(
    r'<button[^>]*id="btn-pdf"[^>]*>.*?Gerar PDF.*?</button>',
    '<button class="btn btn-pdf" onclick="gerarPDFPanorama()">Gerar PDF</button>',
    c, flags=re.IGNORECASE | re.DOTALL
)

# 3. Remove o script de clonagem antigo (que pode estar causando conflito)
c = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*// Seleciona todos os botões.*?</script>', '', c, flags=re.DOTALL)

# 4. Injeta a função gerarPDFPanorama no final do HTML
script_final = """
    <script>
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

if '</body>' in c:
    c = c.replace('</body>', script_final + '\n</body>', 1)
else:
    c += script_final

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão Voltar transformado em botão real e função PDF isolada!")
