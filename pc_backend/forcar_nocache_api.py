c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# Modifica o fetch para adicionar cache: 'no-store' e um timestamp
if "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN')" in c:
    c = c.replace(
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN')",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN&_t=' + Date.now(), { cache: 'no-store' })"
    )
    print("[OK] Frontend forçado a ignorar cache na API!")

# Garante que o texto do limite (50% da RCL) seja atualizado dinamicamente
if "document.getElementById('comp-limite')" in c and "lbl-pct-limite" not in c:
    # Se o ID lbl-pct-limite não existe no HTML, precisamos adicioná-lo primeiro
    c = c.replace(
        "<td>Limite Resolução Cofen 814/2026 (50% da RCL)</td>",
        "<td>Limite Resolução Cofen 814/2026 (<span id='lbl-pct-limite'>50%</span> da RCL)</td>"
    )
    c = c.replace(
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual);",
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual); const lbl = document.getElementById('lbl-pct-limite'); if(lbl) lbl.innerText = (dados.limite_pct*100).toFixed(2).replace('.', ',') + '%';"
    )
    print("[OK] JS do limite atualizado para mostrar o percentual dinâmico!")

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML ajustado com sucesso!")
