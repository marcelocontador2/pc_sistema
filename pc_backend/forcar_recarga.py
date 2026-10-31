c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Garante que o fetch da API tenha no-cache e timestamp (se já não tiver)
if "cache: 'no-store'" not in c:
    c = c.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?_t=' + Date.now(), { cache: 'no-store' })"
    )
    c = c.replace(
        "fetch('/api/custo_pessoal/' + periodo + '?_t=' + Date.now())",
        "fetch('/api/custo_pessoal/' + periodo + '?_t=' + Date.now(), { cache: 'no-store' })"
    )

# 2. Garante que a função 'carregar()' seja chamada ao carregar a página (se não estiver)
if "window.onload = carregar" not in c and "DOMContentLoaded" not in c:
    # Se não tem nenhum dos dois, injeta no final do script
    c = c.replace(
        "</script>",
        "window.addEventListener('DOMContentLoaded', function() { carregar(); carregarHistorico(); });\n</script>"
    )

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] Frontend forçado a buscar dados novos na API!")
