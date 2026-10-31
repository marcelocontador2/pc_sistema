c = open('../pc_frontend/analise_custo_pessoal.html', encoding='utf-8-sig').read()

# 1. Trocar textos LRF por Resolução Cofen
c = c.replace("Custo de Pessoal x Limite da LRF (Art. 19)", "Custo de Pessoal x Limite da Resolução Cofen 814/2026")
c = c.replace("(=) Margem Disponível (Limite LRF - Custo)", "(=) Margem Disponível (Limite Resolução Cofen 814/2026 - Custo)")
c = c.replace("<td>Limite LRF (50% da RCL)</td>", "<td>Limite Resolução Cofen 814/2026 (<span id='lbl-pct-limite'>50%</span> da RCL)</td>")

# 2. Adicionar ?entidade=COREN na chamada da API
c = c.replace(
    "fetch('/api/custo_pessoal/' + periodo)",
    "fetch('/api/custo_pessoal/' + periodo + '?entidade=COREN')"
)

# 3. (Opcional) Garantir que o texto do limite seja atualizado dinamicamente no JS, se existir
if "lbl-pct-limite" in c:
    # Se o JS já atualiza comp-limite, vamos adicionar a atualização do label
    c = c.replace(
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual);",
        "document.getElementById('comp-limite').innerText = fmt(dados.limite_atual); const lbl = document.getElementById('lbl-pct-limite'); if(lbl) lbl.innerText = (dados.limite_pct*100).toFixed(2).replace('.', ',') + '%';"
    )

open('../pc_frontend/analise_custo_pessoal.html', 'w', encoding='utf-8').write(c)
print('[OK] HTML ajustado: textos LRF trocados por Resolução Cofen e API com entidade=COREN!')
