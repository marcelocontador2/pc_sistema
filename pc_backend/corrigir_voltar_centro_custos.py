c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# Substitui o link do botão Voltar
c = c.replace(
    '<a href="/analise_custo_pessoal" class="btn btn-voltar">← Voltar</a>',
    '<a href="/" class="btn btn-voltar">← Voltar</a>'
)

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão Voltar agora aponta para o menu principal!")
