arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Âncora garantida: do comentário do bloco 7 até o comentário do bloco 8 (ou fim)
padrao = re.compile(
    r"(//\s*7\.\s*COMPARATIVO\s+DE\s+RECEITAS.*?)(?=\n\s*//\s*8\.|\Z)",
    re.DOTALL | re.IGNORECASE
)

m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 7 não encontrado. Confirme se o template tem '// 7. COMPARATIVO DE RECEITAS'.")
    raise SystemExit

bloco_original = m.group(0)
print("--- Bloco 7 original (primeiras 20 linhas) ---")
print("\n".join(bloco_original.splitlines()[:20]))
print("-----------------------------------------------")

novo_bloco = """// 7. COMPARATIVO DE RECEITAS (consolidado por Regional)
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

    // --- Consolidação por Regional ---
    // Tenta múltiplos nomes de array no JSON
    const listaRegional =
        crec.por_regional ||
        crec.desdobramento_codm ||
        crec.codm ||
        crec.regionais ||
        crec.por_codm ||
        [];

    if (Array.isArray(listaRegional) && listaRegional.length) {
        const mapa = new Map();
        listaRegional.forEach(r => {
            const key = (
                r.regional ||
                r.nome_regional ||
                r.regiao ||
                r.ds_regional ||
                r.Regional ||
                'NÃO INFORMADO'
            ).toString().trim().toUpperCase();

            const vAt = Number(
                r.atual ?? r.valor_atual ?? r.vl_atual ??
                r.vl_movimento_atual ?? r.movimento_atual ?? 0
            );
            const vAn = Number(
                r.anterior ?? r.valor_anterior ?? r.vl_anterior ??
                r.vl_movimento_anterior ?? r.movimento_anterior ?? 0
            );

            if (!mapa.has(key)) {
                mapa.set(key, { regional: key, atual: 0, anterior: 0 });
            }
            const item = mapa.get(key);
            item.atual += vAt;
            item.anterior += vAn;
        });

        const rows = [];
        [...mapa.values()]
            .sort((a, b) => b.atual - a.atual)
            .forEach(item => {
                rows.push([
                    item.regional,
                    moeda(item.atual),
                    moeda(item.anterior),
                    varPct(item.atual, item.anterior)
                ]);
            });

        const totAt = [...mapa.values()].reduce((s, i) => s + i.atual, 0);
        const totAn = [...mapa.values()].reduce((s, i) => s + i.anterior, 0);
        rows.push(['TOTAL', moeda(totAt), moeda(totAn), varPct(totAt, totAn)]);

        H += sub('Comparativo por Regional');
        H += tab(['Regional','Atual','Anterior','Var. (%)'], rows);
    } else {
        H += '<p>Sem dados de desdobramento por regional.</p>';
    }
} else {
    H += '<p>Módulo não encontrado.</p>';
}
"""

html = html.replace(bloco_original, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Bloco 7 substituído e consolidado por regional.")
