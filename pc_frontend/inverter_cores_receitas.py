c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# Inverte as cores na função renderizarTabela
c = c.replace(
    "const cor = variacao >= 0 ? '#dc3545' : '#28a745';",
    "const cor = variacao >= 0 ? '#28a745' : '#dc3545';"
)

# Inverte as cores da linha de total também
c = c.replace(
    "const corTotal = varTotal >= 0 ? '#dc3545' : '#28a745';",
    "const corTotal = varTotal >= 0 ? '#28a745' : '#dc3545';"
)

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Cores das variações invertidas na tabela de receitas!")
