arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Âncora tolerante: procura o título renderizado OU o comentário
padrao = re.compile(
    r"(H\s*\+=\s*['\"]<h3>\s*Desdobramento\s+por\s+CODM.*?)(?=\n\s*//\s*\d+\.|\n\s*H\s*\+=\s*tit\(|\Z)",
    re.DOTALL | re.IGNORECASE
)

m = padrao.search(html)
if not m:
    print("[ERRO] Ainda não encontrei. Rode o Select-String e me mande o resultado.")
    raise SystemExit

bloco_original = m.group(0)
print("--- Trecho original localizado ---")
print(bloco_original[:600])
print("----------------------------------")

novo_bloco = """H += '<h3>Desdobramento por CODM (consolidado por Regional)</h3>';
H += '<div class="desc">Movimentações agrupadas por regional, sem repetição.</div>';
const codm = unwrap(D.desdobramento_codm) || D.codm || D.receitas_codm || [];
if (Array.isArray(codm) && codm.length) {
    const mapa = new Map();
    codm.forEach(r => {
        const key = (
            r.regional || r.nome_regional || r.regiao ||
            r.ds_regional || r.Regional || 'NÃO INFORMADO'
        ).toString().trim().toUpperCase();
        const at = Number(r.atual ?? r.valor_atual ?? r.vl_atual ?? r.vl_movimento_atual ?? 0);
        const an = Number(r.anterior ?? r.valor_anterior ?? r.vl_anterior ?? r.vl_movimento_anterior ?? 0);
        if (!mapa.has(key)) mapa.set(key, { regional: key, atual: 0, anterior: 0 });
        const item = mapa.get(key);
        item.atual += at;
        item.anterior += an;
    });
    const rows = [];
    [...mapa.values()].sort((a,b)=>b.atual-a.atual).forEach(item => {
        rows.push([item.regional, moeda(item.atual), moeda(item.anterior), varPct(item.atual, item.anterior)]);
    });
    const totAt = [...mapa.values()].reduce((s,i)=>s+i.atual,0);
    const totAn = [...mapa.values()].reduce((s,i)=>s+i.anterior,0);
    rows.push(['TOTAL', moeda(totAt), moeda(totAn), varPct(totAt, totAn)]);
    H += tab(['Regional','Atual','Anterior','Var. (%)'], rows);
} else {
    H += '<p>Sem dados de desdobramento por CODM.</p>';
}
"""

html = html.replace(bloco_original, novo_bloco)
with open(arq, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Bloco consolidado por regional.")
