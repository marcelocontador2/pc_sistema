c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Adiciona um ID no <td> do percentual (que estava fixo em 50,00%)
c = c.replace(
    '<td id="comp-limite">0,00</td>\n                            <td>50,00%</td>',
    '<td id="comp-limite">0,00</td>\n                            <td id="comp-pct-limite">50,00%</td>'
)

# 2. Atualiza o JavaScript para preencher o percentual do limite
if "document.getElementById('comp-pct-limite')" not in c:
    c = c.replace(
        "document.getElementById('comp-limite').innerText = fmt(limite);",
        "document.getElementById('comp-limite').innerText = fmt(limite);\n            const pctLimite = document.getElementById('comp-pct-limite'); if(pctLimite) pctLimite.innerText = fmtPct((limite/rcl)*100);\n            const lblLimite = document.getElementById('lbl-pct-limite'); if(lblLimite) lblLimite.innerText = fmtPct((limite/rcl)*100);"
    )

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML e JS corrigidos! O percentual do limite agora é dinâmico.")
