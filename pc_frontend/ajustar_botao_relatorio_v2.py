c = open('analise_centro_custos.html', encoding='utf-8-sig').read()

# Substitui o link do botão "Gerar PDF" para apontar para o relatório v2
c = c.replace(
    "window.open('/relatorio_centro_custos?id=' + check.value, '_blank');",
    "window.open('/relatorio_centro_custos_v2?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');"
)

# Se não encontrar o texto exato, tenta uma substituição mais flexível
import re
c = re.sub(
    r"window\.open\('/relatorio_centro_custos\?id=' \+ check\.value, '_blank'\);",
    "window.open('/relatorio_centro_custos_v2?periodo_atual=' + encodeURIComponent(check.parentElement.querySelector('strong').innerText), '_blank');",
    c
)

open('analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Gerar PDF' agora aponta para o relatório v2!")
