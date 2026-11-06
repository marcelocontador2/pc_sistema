arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Substitui o bloco do DFC
padrao = re.compile(
    r"(// 5\. ANÁLISE DFC.*?H \+= tab\(\['Item','Atual','Anterior'\], rows\);\s*\}\);.*?\} else \{ H \+= '<p>Módulo não encontrado\.</p>'; \})",
    re.DOTALL
)

nova_secao = '''// 5. ANÁLISE DFC
H += tit(5, 'Análise do Fluxo de Caixa');
H += '<div class="desc">Demonstração do Fluxo de Caixa (método direto).</div>';
const dfc = unwrap(D.analise_dfc);
if (dfc) {
    const blocos = [
        ['Fluxo Operacional', dfc.operacional],
        ['Fluxo de Investimento', dfc.investimento],
        ['Fluxo de Financiamento', dfc.financiamento],
        ['Apuração de Caixa', dfc.caixa]
    ];
    blocos.forEach(([titulo, obj]) => {
        if (!obj) return;
        H += sub(titulo);
        const rows = [];
        Object.keys(obj).forEach(k => {
            const v = obj[k];
            if (v && typeof v === 'object' && 'atual' in v) {
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
    print("[OK] Seção do DFC atualizada (com coluna Var. % em todas as sub-tabelas).")
else:
    print("[ERRO] Não encontrei o bloco do DFC no template.")
