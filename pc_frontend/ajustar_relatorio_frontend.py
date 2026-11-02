c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Ajusta os cards para exibir "N/A" quando não houver dados anteriores
c = c.replace(
    "document.getElementById('kpi-total-anterior').innerText = 'Anterior: R$ ' + fmt(d.anterior.total);",
    "document.getElementById('kpi-total-anterior').innerText = d.anterior.total > 0 ? 'Anterior: R$ ' + fmt(d.anterior.total) : 'N/A (sem dados anteriores)';"
)

c = c.replace(
    "document.getElementById('kpi-media-anterior').innerText = 'Anterior: R$ ' + fmt(d.anterior.media_mensal);",
    "document.getElementById('kpi-media-anterior').innerText = d.anterior.media_mensal > 0 ? 'Anterior: R$ ' + fmt(d.anterior.media_mensal) : 'N/A (sem dados anteriores)';"
)

# Ajusta a variação para não mostrar 0% quando não houver dados anteriores
c = c.replace(
    "varEl.innerText = (d.variacao_pct >= 0 ? '▲' : '▼') + ' ' + fmtPct(Math.abs(d.variacao_pct)) + ' vs. Período Anterior';",
    "if (d.anterior.total === 0) { varEl.innerText = 'Sem dados para comparação'; varEl.className = 'variation'; } else { varEl.innerText = (d.variacao_pct >= 0 ? '▲' : '▼') + ' ' + fmtPct(Math.abs(d.variacao_pct)) + ' vs. Período Anterior'; varEl.className = 'variation ' + (d.variacao_pct >= 0 ? 'positive' : 'negative'); }"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Frontend ajustado para exibir N/A quando não houver dados anteriores!")
