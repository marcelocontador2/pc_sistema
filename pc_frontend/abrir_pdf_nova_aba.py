c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# Substitui a navegação na mesma aba por abertura em nova aba
antigo = "window.location.href = '/gerar_pdf_comparativo_receitas?periodo_atual=' + encodeURIComponent(periodo);"
novo = "window.open('/gerar_pdf_comparativo_receitas?periodo_atual=' + encodeURIComponent(periodo), '_blank');"

if antigo in c:
    c = c.replace(antigo, novo)
    open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
    print("[OK] O PDF agora abrirá em uma nova aba!")
else:
    print("[AVISO] Trecho não encontrado. Tentando versão flexível...")
    # Se o arquivo tiver sido recriado, pode ser que a linha seja ligeiramente diferente
    if "window.location.href" in c:
        c = c.replace(
            "window.location.href = '/gerar_pdf_comparativo_receitas?periodo_atual=' + encodeURIComponent(periodo);",
            "window.open('/gerar_pdf_comparativo_receitas?periodo_atual=' + encodeURIComponent(periodo), '_blank');"
        )
        open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
        print("[OK] Substituição realizada via fallback.")
    else:
        print("[ERRO] Não foi possível encontrar a função gerarPDF.")
