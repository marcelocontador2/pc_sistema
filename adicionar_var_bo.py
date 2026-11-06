arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

padrao = re.compile(
    r"(// 3\. ANÁLISE BO.*?H \+= tab\(\['Indicador','Período Atual','Período Anterior'\], rows\);.*?\} else \{ H \+= '<p>Módulo não encontrado\.</p>'; \})",
    re.DOTALL
)

nova_secao = '''// 3. ANÁLISE BO
H += tit(3, 'Análise do Balanço Orçamentário');
H += '<div class="desc">Comparativo das receitas e despesas orçamentárias.</div>';
const bo = unwrap(D.analise_orcamentaria);
if (bo) {
    const campos = [
        {label:'Receita Realizada', key:'receita_realizada', isPct:false},
        {label:'Despesa Empenhada', key:'despesa_empenhada', isPct:false},
        {label:'Superávit/Déficit', key:'superavit', isPct:false},
        {label:'Restos a Pagar', key:'restos_pagar', isPct:false},
        {label:'Receita Orçada', key:'receita_orcada', isPct:false},
        {label:'Despesa Orçada', key:'despesa_orcada', isPct:false},
        {label:'% Realização Receitas', key:'pct_receita', isPct:true},
        {label:'% Realização Despesas', key:'pct_despesa', isPct:true}
    ];
    const rows = [];
    campos.forEach(c => {
        const at = bo.atual ? bo.atual[c.key] : null;
        const an = bo.anterior ? bo.anterior[c.key] : null;
        const fAt = c.isPct ? pct(at) : moeda(at);
        const fAn = c.isPct ? pct(an) : moeda(an);
        // Calcula variação percentual entre os períodos (para campos que não são %)
        let varStr = '-';
        if (!c.isPct && at !== null && an !== null && an !== 0) {
            const v = ((at - an) / Math.abs(an)) * 100;
            varStr = (v >= 0 ? '+' : '') + v.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
        }
        rows.push([c.label, fAt, fAn, varStr]);
    });
    H += tab(['Indicador','Período Atual','Período Anterior','Var. (%)'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }'''

if padrao.search(html):
    html = padrao.sub(lambda m: nova_secao, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção do BO atualizada (com coluna Var. %).")
else:
    print("[ERRO] Não encontrei o bloco do BO no template.")
