c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

c = c.replace(
    "window.open('/relatorio_comparativo_receitas?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');",
    "window.open('/relatorio_comparativo_receitas_v2?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');"
)

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Gerar PDF' aponta para o novo relatório!")
