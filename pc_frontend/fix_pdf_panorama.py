import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# 1. Cria a funcao gerarPDF() (se nao existir)
funcao_pdf = '''
function gerarPDF() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) {
        alert("Selecione um item no histórico para gerar o PDF.");
        return;
    }
    window.open('/gerar_pdf_panorama/' + check.value, '_blank');
}
'''

# 2. Verifica se a funcao ja existe
if "function gerarPDF()" not in s:
    # Insere a funcao antes do </script>
    s = s.replace("</script>", funcao_pdf + "\n</script>")
    print("OK: Funcao gerarPDF() injetada com sucesso!")
else:
    print("OK: Funcao gerarPDF() ja existe.")

# 3. Garante que o botao btn-pdf esteja vinculado no DOMContentLoaded
if "document.getElementById('btn-pdf')" not in s:
    # Adiciona o vinculo no DOMContentLoaded
    s = s.replace(
        "const btnSalvar = document.getElementById('btn-salvar');",
        "const btnPdf = document.getElementById('btn-pdf');\n    if (btnPdf) btnPdf.addEventListener('click', gerarPDF);\n    \n    const btnSalvar = document.getElementById('btn-salvar');"
    )
    print("OK: Vinculo do botao btn-pdf adicionado no DOMContentLoaded.")
else:
    print("OK: O botao btn-pdf ja tem vinculo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
