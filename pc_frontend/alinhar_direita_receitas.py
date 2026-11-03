c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Alinhar o cabeçalho da tabela
c = c.replace(
    "<th>Grupo de Receita</th><th>Período Atual (R$)</th><th>Período Anterior (R$)</th><th>Variação (R$)</th><th>Variação (%)</th>",
    "<th>Grupo de Receita</th><th class='text-right'>Período Atual (R$)</th><th class='text-right'>Período Anterior (R$)</th><th class='text-right'>Variação (R$)</th><th class='text-right'>Variação (%)</th>"
)

# 2. Alinhar as linhas de dados
c = c.replace(
    "<td>${g.nome}</td>\n                    <td>${fmt(g.realizado)}</td>\n                    <td>${fmt(valorAnterior)}</td>\n                    <td style=\"color: ${cor};\">${fmt(variacao)}</td>\n                    <td style=\"color: ${cor};\">${fmt(variacaoPct)}%</td>",
    "<td>${g.nome}</td>\n                    <td class='text-right'>${fmt(g.realizado)}</td>\n                    <td class='text-right'>${fmt(valorAnterior)}</td>\n                    <td class='text-right' style=\"color: ${cor};\">${fmt(variacao)}</td>\n                    <td class='text-right' style=\"color: ${cor};\">${fmt(variacaoPct)}%</td>"
)

# 3. Alinhar a linha de total
c = c.replace(
    "<td>TOTAL</td>\n                <td>${fmt(totalAtual)}</td>\n                <td>${fmt(totalAnterior)}</td>\n                <td style=\"color: ${corTotal};\">${fmt(varTotal)}</td>\n                <td style=\"color: ${corTotal};\">${fmt(varTotalPct)}%</td>",
    "<td>TOTAL</td>\n                <td class='text-right'>${fmt(totalAtual)}</td>\n                <td class='text-right'>${fmt(totalAnterior)}</td>\n                <td class='text-right' style=\"color: ${corTotal};\">${fmt(varTotal)}</td>\n                <td class='text-right' style=\"color: ${corTotal};\">${fmt(varTotalPct)}%</td>"
)

# 4. Garantir que a classe .text-right existe no CSS
if '.text-right' not in c:
    c = c.replace('</style>', '\n        .text-right { text-align: right; }\n    </style>')

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Valores numéricos alinhados à direita!")
