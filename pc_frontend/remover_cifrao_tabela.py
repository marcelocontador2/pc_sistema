c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Remove o "R$ " dos valores nas tabelas (mantém apenas os números)
c = c.replace('<td class="text-right">R$ ${fmt(c.valor)}</td>', '<td class="text-right">${fmt(c.valor)}</td>')
c = c.replace('<td class="text-right">R$ ${fmt(c.valor)}</td>', '<td class="text-right">${fmt(c.valor)}</td>')

# Verifica se há outros "R$ " em células de tabela
c = c.replace('R$ ${fmt', '${fmt')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] Removido 'R$' dos valores das tabelas!")
