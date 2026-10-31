c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Garantir que o texto do limite na tabela seja dinâmico
c = c.replace(
    "Limite Resolução Cofen 814/2026 (50% da RCL)",
    "Limite Resolução Cofen 814/2026 (<span id='lbl-pct-limite'>50%</span> da RCL)"
)

# 2. Garantir que o texto "Margem Disponível" não tenha o 50% fixo (se houver)
c = c.replace(
    "(=) Margem Disponível (Limite LRF - Custo)",
    "(=) Margem Disponível (Limite Resolução Cofen 814/2026 - Custo)"
)

# 3. Injetar o JS para preencher o percentual do limite dinamicamente
if "const lbl = document.getElementById('lbl-pct-limite');" not in c:
    c = c.replace(
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual);",
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual); const lbl = document.getElementById('lbl-pct-limite'); if(lbl) lbl.innerText = (dados.limite_pct*100).toFixed(2).replace('.', ',') + '%';"
    )

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print('[OK] Frontend ajustado para exibir o percentual dinâmico!')
