c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Remover o chumbo do COREN e voltar a chamar a API de forma limpa (com no-cache)
c = c.replace(
    "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN&_t=' + Date.now(), { cache: 'no-store' })",
    "fetch('/api/custo_pessoal/' + periodo + '?_t=' + Date.now(), { cache: 'no-store' })"
)

# 2. Se ainda tiver resquícios da URL antiga
c = c.replace(
    "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN')",
    "fetch('/api/custo_pessoal/' + periodo + '?_t=' + Date.now(), { cache: 'no-store' })"
)

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print('[OK] Frontend limpo! O backend agora decide a entidade.')
