c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

c = c.replace(
    "Revisar os contratos e processos dos 3 maiores centros de custo, dado o alto grau de concentração.",
    "Monitorar os contratos e processos dos 3 maiores centros de custo, dado o alto grau de concentração."
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Texto da recomendação alterado para 'Monitorar'!")
