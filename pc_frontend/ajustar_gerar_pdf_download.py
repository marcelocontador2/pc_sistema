c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# Substitui a função gerarPDF para chamar a rota de geração de PDF (download)
antigo = """        function gerarPDF() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico para gerar o PDF.'); return; }
            const periodo = check.parentElement.querySelector('strong').innerText;
            window.open('/relatorio_comparativo_receitas_v2?periodo_atual=' + encodeURIComponent(periodo), '_blank');
        }"""

novo = """        function gerarPDF() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico para gerar o PDF.'); return; }
            const periodo = check.parentElement.querySelector('strong').innerText;
            // Abre a rota que gera o PDF via Playwright e faz o download
            window.location.href = '/gerar_pdf_comparativo_receitas?periodo_atual=' + encodeURIComponent(periodo);
        }"""

if antigo in c:
    c = c.replace(antigo, novo)
    open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Função gerarPDF ajustada para download do PDF!")
else:
    print("[AVISO] Função antiga não encontrada. Tentando substituição flexível...")
    import re
    padrao = r'function gerarPDF\(\) \{.*?\n        \}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, novo, c, flags=re.DOTALL)
        open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
        print("[OK] Função substituída via regex!")
    else:
        print("[ERRO] Não foi possível encontrar a função gerarPDF.")
