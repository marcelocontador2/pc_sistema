arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Localiza o bloco do comparativo de receitas
padrao = re.compile(
    r"(//\s*COMPARATIVO\s+DE\s+RECEITAS.*?)(?=\n\s*//\s*\d+\.)",
    re.DOTALL | re.IGNORECASE
)

m = padrao.search(html)
if not m:
    print("[ERRO] Bloco de comparativo de receitas não encontrado.")
    raise SystemExit

bloco_original = m.group(0)

# Nova lógica: consolidar por regional antes de montar as linhas
novo_bloco = """// COMPARATIVO DE RECEITAS (consolidado por regional)
H += tit(X, 'Comparativo de Receitas por Regional');
H += '<div class="desc">Valores consolidados por regional (sem repetição).</div>';
const rec = unwrap(D.comparativo_receitas) || [];
if (Array.isArray(rec) && rec.length) {
    // Consolida por regional
    const mapa = new Map();
    rec.forEach(r => {
        const key = (r.regional || r.nome_regional || r.regiao || 'NÃO INFORMADO').toString().trim().toUpperCase();
        const at = Number(r.atual ?? r.valor_atual ?? 0);
        const an = Number(r.anterior ?? r.valor_anterior ?? 0);
        if (!mapa.has(key)) {
            mapa.set(key, { regional: key, atual: 0, anterior: 0 });
        }
        const item = mapa.get(key);
        item.atual += at;
        item.anterior += an;
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
    // Linha de total
    const totAt = [...mapa.values()].reduce((s, i) => s + i.atual, 0);
    const totAn = [...mapa.values()].reduce((s, i) => s + i.anterior, 0);
    rows.push(['TOTAL', moeda(totAt), moeda(totAn), varPct(totAt, totAn)]);
    H += tab(['Regional','Atual','Anterior','Var. (%)'], rows);
} else {
    H += '<p>Sem dados de receitas por regional.</p>';
}
"""

# Substitui o bloco inteiro
html = html.replace(bloco_original, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Comparativo de receitas consolidado por regional.")
