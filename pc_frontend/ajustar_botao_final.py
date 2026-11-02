c = open('analise_centro_custos.html', encoding='utf-8-sig').read()
c = c.replace(
    "window.open('/relatorio_centro_custos_v2?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');",
    "window.open('/relatorio_final?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');"
)
open('analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão apontando para /relatorio_final!")
