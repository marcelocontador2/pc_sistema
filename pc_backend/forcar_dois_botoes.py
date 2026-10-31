c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()
# 1. Substituir o botão usando texto exato
if '>Gerar PDF</button>' in c:
    c = c.replace(
        '>Gerar PDF</button>',
        '>Gerar PDF (Resumo)</button>\n<button class="btn" onclick="gerarPDFCompleto()" style="background-color: #17a2b8; color: white; margin-left: 10px;">Gerar PDF (Completo)</button>'
    )
    print("[OK] Botões substituídos por texto exato!")
# 2. Adicionar a função JS do PDF Completo
if "function gerarPDFCompleto()" not in c:
    js_func = """
        function gerarPDFCompleto() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico para gerar o PDF Completo.'); return; }
            window.open('/gerar_pdf_completo_custo_pessoal?id=' + check.value, '_blank');
        }
    """
    # Injeta a função antes do fechamento do último script
    pos = c.rfind("</script>")
    if pos != -1:
        c = c[:pos] + js_func + "\n" + c[pos:]
        print("[OK] Função gerarPDFCompleto() injetada!")
open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
