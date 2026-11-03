c = open('relatorio_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Ajusta o card de Receita Realizada
c = c.replace(
    'document.getElementById(\'kpi-realizado-anterior\').innerText = \'vs. \' + fmtMi(an.realizado_total);',
    'document.getElementById(\'kpi-realizado-anterior\').innerText = \'Período Anterior: \' + fmtMi(an.realizado_total);'
)

# 2. Ajusta o card de Receita Orçada
c = c.replace(
    'document.getElementById(\'kpi-orcado-anterior\').innerText = \'vs. \' + fmtMi(an.orcado_total);',
    'document.getElementById(\'kpi-orcado-anterior\').innerText = \'Período Anterior: \' + fmtMi(an.orcado_total);'
)

open('relatorio_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Cards ajustados com referência explícita ao período anterior!")
