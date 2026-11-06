arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

padrao = re.compile(
    r"(//\s*7\.\s*COMPARATIVO\s+DE\s+RECEITAS.*?)(?=\n\s*//\s*8\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 7 não encontrado.")
    raise SystemExit

bloco_original = m.group(0)

novo_bloco = """// 7. COMPARATIVO DE RECEITAS
H += tit(7, 'Comparativo de Receitas');
H += '<div class="desc">Comparativo consolidado de receitas.</div>';
const crec = unwrap(D.comparativo_receitas);
if (crec) {
    const at = crec.atual || {};
    H += sub('Resumo');
    H += tab(['Indicador','Valor'], [
        ['Receita Orçada', moeda(at.orcado_total)],
        ['Receita Realizada', moeda(at.realizado_total)],
        ['% Execução', pct(at.percentual_total)]
    ]);
    if (at.grupos && at.grupos.length) {
        H += sub('Composição por Grupo');
        H += tab(['Grupo','Orçado','Realizado','%'],
            at.grupos.map(g => [g.nome, moeda(g.orcado), moeda(g.realizado), pct(g.percentual)]));
    }
    // --- Consolidado por Regional / Estado (usando o campo 'nome') ---
    if (at.cores && at.cores.length) {
        const mapa = new Map();
        at.cores.forEach(c => {
            const key = (c.nome || c.regional || 'NÃO INFORMADO').toString().trim().toUpperCase();
            const orc = Number(c.orcado || 0);
            const real = Number(c.realizado || 0);
            if (!mapa.has(key)) mapa.set(key, { regional: key, orcado: 0, realizado: 0 });
            const item = mapa.get(key);
            item.orcado += orc;
            item.realizado += real;
        });
        const rows = [];
        let totOrc = 0;
        let totReal = 0;
        
        // ORDENAÇÃO ALFABÉTICA
        [...mapa.values()]
            .sort((a, b) => a.regional.localeCompare(b.regional))
            .forEach(item => {
                const perc = item.orcado ? (item.realizado / item.orcado * 100) : 0;
                const nomeFormatado = item.regional.charAt(0) + item.regional.slice(1).toLowerCase();
                rows.push([nomeFormatado, moeda(item.orcado), moeda(item.realizado), pct(perc)]);
                
                // Acumula os totais
                totOrc += item.orcado;
                totReal += item.realizado;
            });
            
        // Adiciona a linha de TOTAL
        const percTotal = totOrc ? (totReal / totOrc * 100) : 0;
        rows.push(['TOTAL', moeda(totOrc), moeda(totReal), pct(percTotal)]);

        H += sub('Desdobramento por Regional');
        H += tab(['Regional','Orçado','Realizado','%'], rows);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }
"""

html = html.replace(bloco_original, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Bloco 7 atualizado com linha de TOTAL.")
