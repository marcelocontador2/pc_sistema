c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Filtra os centros no JavaScript para não exibir "Centro de Custo" ou "Centro de Custo x Conta"
c = c.replace(
    "const ordenados = Object.keys(mapa).sort((a, b) => mapa[b].atual - mapa[a].atual);",
    "const ordenados = Object.keys(mapa).filter(nome => !nome.includes('Centro de Custo')).sort((a, b) => mapa[b].atual - mapa[a].atual);"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Frontend ajustado para não exibir a linha 'Centro de Custo x Conta'!")
