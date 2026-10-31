import re
c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()
# 1. Substitui o botão atual por dois botões (Resumo e Completo)
# Usamos regex para encontrar o botão independentemente de pequenas variações de espaços
c = re.sub(
    r'<button[^>]*onclick="gerarPDF\(\)"[^>]*>Gerar PDF</button>',
    '<button class="btn" onclick="gerarPDF()" style="margin-right: 10px;">Gerar PDF (Resumo)</button>\n<button class="btn" onclick="gerarPDFCompleto()">Gerar PDF (Completo)</button>',
    c
)
# 2. Cria a função gerarPDFCompleto() baseada na função gerarPDF() existente
if "function gerarPDFCompleto()" not in c:
    # Encontra a função gerarPDF atual no código
    match = re.search(r'function gerarPDF\(\)\s*\{.*?\}', c, re.DOTALL)
    if match:
        func_antiga = match.group(0)
        # Clona a função, muda o nome e a URL
        func_nova = func_antiga.replace('gerarPDF()', 'gerarPDFCompleto()')
        func_nova = func_nova.replace('/gerar_pdf_custo_pessoal', '/gerar_pdf_completo_custo_pessoal')
        # Insere a nova função logo após a antiga
        c = c.replace(func_antiga, func_antiga + "\n\n        " + func_nova)
        print("[OK] Função gerarPDFCompleto() criada com sucesso!")
    else:
        print("[AVISO] Não foi possível encontrar a função gerarPDF() original. Adicionando versão padrão.")
        # Fallback caso a função não esteja no formato esperado
        fallback_js = """
        function gerarPDFCompleto() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            window.open('/gerar_pdf_completo_custo_pessoal?id=' + check.value, '_blank');
        }
        """
        c = c.replace("</script>", fallback_js + "\n</script>")
open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado com os dois botões de PDF!")
