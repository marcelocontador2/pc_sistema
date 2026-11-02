c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

# Substitui o gradiente diagonal por uma tarja retangular
c = c.replace(
    "background: linear-gradient(135deg, #fff 60%, var(--primary) 60%);",
    "background: linear-gradient(to right, #fff 60%, var(--primary) 60%);"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Fundo da capa alterado para tarja retangular!")
