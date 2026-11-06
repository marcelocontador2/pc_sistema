arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Substitui o bloco do BF (da linha "// 4. ANÁLISE BF" até o "else" final)
padrao = re.compile(
    r"(// 4\. ANÁLISE BF.*?H \+= tab\(\['Item','Atual','Anterior'\], rows\);\s*\}\);.*?\} else \{ H \+= '<p>Módulo não encontrado\.</p>'; \})",
    re.DOTALL
)

nova_secao = '''// 4. ANÁLISE BF
H += tit(4, 'Análise do Balanço Financeiro');
H += '<div class="desc">Movimentação financeira consolidada.</div>';
const bf = unwrap(D.analise_financeira_bf);
if (bf) {
    const blocos = [
        ['Receitas', bf.receitas],
        ['Despesas', bf.despesas],
        ['Extraorçamentário', bf.extra],
        ['Caixa', bf.caixa]
    ];
    blocos.forEach(([titulo, obj]) => {
        if (!obj) return;
        H += sub(titulo);
        const rows = [];
        Object.keys(obj).forEach(k => {
            const v = obj[k];
            if (k === 'detalhes') {
                Object.keys(v).forEach(kk => {
                    const at = v[kk].atual;
                    const an = v[kk].anterior;
                    rows.push(['  ' + kk.replace(/_/g,' ').toUpperCase(), moeda(at), moeda(an), varPct(at, an)]);
                });
            } else if (v && typeof v === 'object' && 'atual' in v) {
                const at = v.atual;
                const an = v.anterior;
                rows.push([k.replace(/_/g,' ').toUpperCase(), moeda(at), moeda(an), varPct(at, an)]);
            }
        });
        H += tab(['Item','Atual','Anterior','Var. (%)'], rows);
    });
} else { H += '<p>Módulo não encontrado.</p>'; }'''

if padrao.search(html):
    html = padrao.sub(lambda m: nova_secao, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção do BF atualizada (com coluna Var. % em todas as sub-tabelas).")
else:
    print("[ERRO] Não encontrei o bloco do BF no template.")
