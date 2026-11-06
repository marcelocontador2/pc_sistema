arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# O texto exato que está no seu arquivo agora (tudo em uma linha ou quebrado)
alvo = "H += tab(['Centro de Custo','Atual','Anterior','Variação'], rows);"

# O código do ranking que queremos inserir logo DEPOIS dessa tabela
codigo_ranking = """
    // 2. Tabela de Ranking (Decrescente)
    H += sub('Ranking de Gastos (Maior para Menor)');
    const ranking = [];
    Object.keys(mapa).forEach(nome => {
        const {at: va} = mapa[nome];
        ranking.push({ nome, valorStr: moeda(va), valorNum: va });
    });
    ranking.sort((a, b) => b.valorNum - a.valorNum);
    const rowsRanking = ranking.map((r, i) => [String(i + 1), r.nome, r.valorStr]);
    H += tab(['#', 'Centro de Custo', 'Gasto Atual'], rowsRanking);
"""

if alvo in html:
    # Substitui a linha original pela linha original + o código do ranking
    html = html.replace(alvo, alvo + "\n" + codigo_ranking)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Tabela de Ranking inserida com sucesso após a tabela original!")
else:
    print("[AVISO] Não encontrei a linha exata da tabela. O arquivo pode ter sido salvo com outro formato. Vou tentar uma abordagem mais flexível...")
    # Tentativa 2: buscar apenas por "Centro de Custo','Atual','Anterior','Variação"
    import re
    padrao = re.compile(r"(H\s*\+=\s*tab\(\['Centro de Custo','Atual','Anterior','Variação'\],\s*rows\);)", re.IGNORECASE)
    m = padrao.search(html)
    if m:
        linha_encontrada = m.group(1)
        html = html.replace(linha_encontrada, linha_encontrada + "\n" + codigo_ranking)
        with open(arq, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Tabela de Ranking inserida com sucesso (abordagem flexível)!")
    else:
        print("[ERRO] Não foi possível encontrar a tabela original. O arquivo pode estar corrompido.")
